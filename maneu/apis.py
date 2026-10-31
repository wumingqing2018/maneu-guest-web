"""
maneu/apis.py

API 视图层：只做参数校验、调用 service、组装 JSON 响应，不直接操作 Model。

统一响应：
    成功 {"status": true,  "message": "...", "content": any}
    失败 {"status": false, "message": "...", "content": {}}   HTTP 400/401/403/404

约定：
    - 请求体一律 application/json
    - 路径含 /auth/ 的接口由 UserMiddleware 拦截并注入 jwt_phone
    - 详情类接口额外校验记录归属（记录 phone 必须等于登录用户）
    - 命名：xxx_verify（免登录扫码） / xxx_list / xxx_detail / 认证类
"""

import json
import logging

from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from common import util_verify, util_jwt
from common.util_sms import send_sms_code
from common.util_wechat import get_miniprogram_token, get_miniprogram_phone

from maneu.service import (
    get_admin_by_id,
    get_order_by_id, get_store_by_id, get_report_by_id, get_repair_by_id,
    get_orders_by_phone, get_reports_by_phone, get_stores_by_phone, get_repairs_by_phone,
    get_guest_by_phone, get_guest_model_by_phone,
    generate_sms_code, save_sms_code, verify_sms_code,
    is_sms_locked, record_sms_fail,
)

logger = logging.getLogger(__name__)

SMS_SEND_COOLDOWN = 60
SMS_SEND_PREFIX = 'sms:send:'


# ============================================================================
# 内部辅助
# ============================================================================

def _parse_json(request):
    """请求体解析为 dict；解析失败或非对象一律返回 {}。"""
    try:
        data = json.loads(request.body or '{}')
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}


def _extract_param(request, key):
    return _parse_json(request).get(key)


def _json_error(message, status_code=400):
    return JsonResponse(
        {'status': False, 'message': message, 'content': {}},
        status=status_code,
    )


def _safe_json(raw, default=None):
    """
    解析 content：dict/list 直接返回；字符串走 json.loads；脏数据返回 default。
    兼容 content 为 TextField（字符串）或 JSONField（对象）。
    """
    if isinstance(raw, (dict, list)):
        return raw
    try:
        return json.loads(raw or '{}')
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else {}


def _check_owner(request, data):
    """
    校验记录归属：record.phone 必须等于当前登录用户。
    历史数据 phone 为空时放行，避免旧记录全部不可访问。
    """
    record_phone = data.get('phone')
    if not record_phone:
        return None
    if record_phone != util_jwt.get_admin_phone_from_request(request):
        return _json_error('无权访问该记录', status_code=403)
    return None


def _paging_params(request):
    """提取 offset / limit，非法值归为 None（表示不分页）。"""
    params = _parse_json(request)

    def _to_int(v):
        try:
            i = int(v)
            return i if i >= 0 else None
        except (TypeError, ValueError):
            return None

    return _to_int(params.get('offset')), _to_int(params.get('limit'))


def _send_verification_code(call, code):
    """发短信，返回 (ok, message)；异常时由调用方回滚验证码与冷却。"""
    try:
        response = send_sms_code(call=call, code=code)
        if response.get('status'):
            return True, '验证码已发送'
        return False, response.get('message', '发送失败')
    except Exception as e:
        logger.exception('发送短信异常：%s', e)
        return False, '系统繁忙，请稍后重试'


def _fetch_phone_with_retry(code, access_token):
    """用微信 code 换手机号；token 失效时刷新一次并重试。"""
    phone_info = get_miniprogram_phone(code, access_token)
    if phone_info.get('status'):
        return phone_info.get('message')

    logger.warning('微信 token 失效，尝试刷新')
    token_data = get_miniprogram_token(force_refresh=True)
    new_token = token_data.get('access_token')
    if not new_token:
        return None

    phone_info = get_miniprogram_phone(code, new_token)
    if phone_info.get('status'):
        return phone_info.get('message')

    logger.error('获取手机号最终失败：%s', phone_info.get('message'))
    return None


def _generate_jwt_for_user(user):
    """为 ORM 用户实例生成 JWT 令牌对。"""
    return {
        'access_token':  util_jwt.generate_access_token(user),
        'refresh_token': util_jwt.generate_refresh_token(user),
    }


def _verify_response(data):
    """扫码验证类接口的公共响应：{time, data: <content 解析结果>}。"""
    return JsonResponse({
        'status': True,
        'message': '请求成功',
        'content': {
            'time': data.get('time'),
            'data': _safe_json(data.get('content')),
        },
    })


def _list_response(getter, request):
    """列表类接口的公共响应；getter(phone, offset, limit) 返回 list。"""
    phone = util_jwt.get_admin_phone_from_request(request)
    offset, limit = _paging_params(request)
    return JsonResponse({
        'status': True,
        'message': '请求成功',
        'content': getter(phone, offset, limit),
    })


def _detail_payload(data):
    """
    详情类接口的公共载荷：记录字段 + 所属机构公开信息。
    content 保持原始 JSON 字符串，由客户端（小程序 parseContent）解析。
    """
    admin = get_admin_by_id(data.get('admin_id')) or {}
    return {
        'time':           data.get('time'),
        'name':           data.get('name'),
        'phone':          data.get('phone'),
        'remark':         data.get('remark'),
        'content':        data.get('content'),
        'admin_name':     admin.get('nickname'),
        'admin_phone':    admin.get('phone'),
        'admin_location': admin.get('location'),
        # 白名单不含 content，故恒为 None；保留键名兼容旧客户端
        'admin_content':  admin.get('content'),
    }


def _detail_handler(getter, request):
    """详情类接口的公共流程：取 code → 查记录 → 校验归属 → 组装响应。"""
    record_id = _extract_param(request, 'code')
    if not util_verify.is_uuid(record_id):
        return _json_error('记录ID无效')

    data = getter(record_id)
    if not data:
        return _json_error('记录不存在', status_code=404)

    err = _check_owner(request, data)
    if err:
        return err

    return JsonResponse({
        'status': True,
        'message': '请求成功',
        'content': _detail_payload(data),
    })


# ============================================================================
# 二、扫码验证（免登录）
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def order_verify(request):
    """订单扫码验证。请求 {"index_id": "<UUID>"}。"""
    index_id = _extract_param(request, 'index_id')
    if not util_verify.is_uuid(index_id):
        return _json_error('请提交正确的参数')

    data = get_order_by_id(index_id)
    if not data:
        return _json_error('记录不存在')
    return _verify_response(data)


@csrf_exempt
@require_http_methods(["POST"])
def store_verify(request):
    """门店扫码验证。请求 {"index_id": "<UUID>"}。"""
    index_id = _extract_param(request, 'index_id')
    if not util_verify.is_uuid(index_id):
        return _json_error('请提交正确的参数')

    data = get_store_by_id(index_id)
    if not data:
        return _json_error('记录不存在')
    return _verify_response(data)


@csrf_exempt
@require_http_methods(["POST"])
def report_verify(request):
    """
    报告扫码验证。请求 {"index_id": "<UUID>"}。

    ⚠️ 结构变更：旧版返回平铺的 od_sph / os_sph 等（历史数据多为 null），
       现改为 data.od.sph / data.os.sph；扫码端需同步读取 content.data.od.sph。
    """
    index_id = _extract_param(request, 'index_id')
    if not util_verify.is_uuid(index_id):
        return _json_error('请提交正确的参数')

    data = get_report_by_id(index_id)
    if not data:
        return _json_error('记录不存在')
    return _verify_response(data)


@csrf_exempt
@require_http_methods(["POST"])
def repair_verify(request):
    """维修记录扫码验证。请求 {"index_id": "<UUID>"}。"""
    index_id = _extract_param(request, 'index_id')
    if not util_verify.is_uuid(index_id):
        return _json_error('请提交正确的参数')

    data = get_repair_by_id(index_id)
    if not data:
        return _json_error('记录不存在')
    return _verify_response(data)


# ============================================================================
# 三、列表（需登录，路径含 /auth/）
# 手机号由 UserMiddleware 注入；可选 offset / limit 分页。
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def order_list(request):
    """当前用户订单列表。"""
    return _list_response(get_orders_by_phone, request)


@csrf_exempt
@require_http_methods(["POST"])
def report_list(request):
    """当前用户报告列表。"""
    return _list_response(get_reports_by_phone, request)


@csrf_exempt
@require_http_methods(["POST"])
def store_list(request):
    """当前用户门店列表。"""
    return _list_response(get_stores_by_phone, request)


@csrf_exempt
@require_http_methods(["POST"])
def repair_list(request):
    """当前用户维修记录列表。"""
    return _list_response(get_repairs_by_phone, request)


# ============================================================================
# 四、详情（需登录，路径含 /auth/）
# 需校验记录归属，仅允许访问本人记录。
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def order_detail(request):
    """订单详情。请求 {"code": "<UUID>"}。"""
    return _detail_handler(get_order_by_id, request)


@csrf_exempt
@require_http_methods(["POST"])
def store_detail(request):
    """门店详情。请求 {"code": "<UUID>"}。"""
    return _detail_handler(get_store_by_id, request)


@csrf_exempt
@require_http_methods(["POST"])
def report_detail(request):
    """报告详情。请求 {"code": "<UUID>"}。"""
    return _detail_handler(get_report_by_id, request)


@csrf_exempt
@require_http_methods(["POST"])
def repair_detail(request):
    """维修记录详情。请求 {"code": "<UUID>"}。"""
    return _detail_handler(get_repair_by_id, request)


@csrf_exempt
@require_http_methods(["POST"])
def guest_detail(request):
    """当前登录用户信息；手机号由 UserMiddleware 注入。"""
    phone = util_jwt.get_admin_phone_from_request(request)
    user = get_guest_by_phone(phone)
    if not user:
        return _json_error('用户不存在', status_code=404)
    return JsonResponse({'status': True, 'message': '请求成功', 'content': user})


@csrf_exempt
@require_http_methods(["POST"])
def guest_update(request):
    """
    TODO: 目前仅返回当前用户信息，尚未实现更新。
    需补齐：读取请求体 → 校验可改字段（nickname 等）→ service 层 update。
    """
    phone = util_jwt.get_admin_phone_from_request(request)
    user = get_guest_by_phone(phone)
    if not user:
        return _json_error('用户不存在', status_code=404)
    return JsonResponse({'status': True, 'message': '请求成功', 'content': user})


# ============================================================================
# 五、认证（免登录）
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def send_sms(request):
    """
    发送短信验证码。请求 {"call": "手机号"}。
    流程：格式校验 → 已注册校验 → 60s 冷却 → 生成并保存 → 发送；
         发送失败时回滚验证码与冷却。
    """
    call = _extract_param(request, 'call')

    if not util_verify.is_call(call):
        return _json_error('请输入正确的手机号')
    if not get_guest_by_phone(call):
        return _json_error('当前账号未注册')

    cooldown_key = f'{SMS_SEND_PREFIX}{call}'
    if cache.get(cooldown_key):
        return _json_error('发送过于频繁，请稍后再试')
    cache.set(cooldown_key, 1, timeout=SMS_SEND_COOLDOWN)

    code = generate_sms_code()
    save_sms_code(call, code)

    ok, msg = _send_verification_code(call, code)
    if not ok:
        cache.delete(f'sms:code:{call}')
        cache.delete(cooldown_key)
        return _json_error(msg)

    return JsonResponse({'status': True, 'message': msg, 'content': {}})


@csrf_exempt
@require_http_methods(["POST"])
def login_by_sms(request):
    """
    短信验证码登录。请求 {"call": "手机号", "code": "6位数字"}。
    失败累计达上限会锁定，需重新获取验证码。
    """
    params = _parse_json(request)
    call = params.get('call')
    code = params.get('code')

    if not util_verify.is_call(call):
        return _json_error('请输入正确的手机号')
    if not util_verify.is_token_6(code):
        return _json_error('验证码格式错误')
    if is_sms_locked(call):
        return _json_error('验证码错误次数过多，请重新获取')
    if not verify_sms_code(call, code):
        record_sms_fail(call)
        return _json_error('验证码错误或已过期')

    user = get_guest_model_by_phone(call)
    if not user:
        return _json_error('该手机号未注册')

    return JsonResponse({
        'status': True,
        'message': '登录成功',
        'content': _generate_jwt_for_user(user),
    })


@csrf_exempt
@require_http_methods(["POST"])
def login_by_wechat(request):
    """微信小程序登录。请求 {"code": "<64位十六进制>"}。"""
    code = _extract_param(request, 'code')
    if not code or not util_verify.is_token_64(code):
        return _json_error('登录失败：请提交正确的微信号')

    token_data = get_miniprogram_token()
    access_token = token_data.get('access_token')
    if not access_token:
        return _json_error('系统错误，无法获取微信授权')

    phone = _fetch_phone_with_retry(code, access_token)
    if phone is None:
        return _json_error('获取手机号失败，请联系管理员')

    user = get_guest_model_by_phone(phone)
    if not user:
        return _json_error('该手机号未注册')

    return JsonResponse({
        'status': True,
        'message': '登录成功',
        'content': _generate_jwt_for_user(user),
    })


@csrf_exempt
@require_http_methods(["POST"])
def refresh_access_token(request):
    """
    刷新令牌。请求 {"refresh_token": "<JWT>"}。
    ⚠️ refresh_token 轮换：旧值刷新后不再保证有效，客户端须保存新值。
    """
    token = _extract_param(request, 'refresh_token')
    if not token:
        return _json_error('缺少 refresh_token', status_code=401)

    payload = util_jwt.verify_token(token, expected_type='refresh')
    if not payload:
        return _json_error('refresh_token 无效或已过期', status_code=401)

    user_phone = payload.get('user_phone')
    if not user_phone:
        return _json_error('payload 中缺少 user_phone', status_code=401)

    user = get_guest_model_by_phone(user_phone)
    if not user:
        return _json_error('用户不存在', status_code=401)

    return JsonResponse({
        'status': True,
        'message': '刷新成功',
        'content': {
            'access_token':  util_jwt.generate_access_token(user),
            'refresh_token': util_jwt.generate_refresh_token(user),
        },
    })


# ============================================================================
# 六、平台校验文件（微信小程序域名校验）
# ============================================================================

def VQwxjTJTH5(request):
    """微信域名校验文件，返回纯文本；内容需与小程序后台一致。"""
    return HttpResponse(
        "c8966dfaa24aa981832913b888981534",
        content_type='text/plain',
    )