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
    - 每个接口自包含：参数校验 → 查库 → 组装响应，不通过公共流程函数委托
"""

import json
import logging

from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from common import util_verify, util_jwt
from common.util_sms import send_sms_code
from common.util_wechat import (
    get_miniprogram_token,
    get_miniprogram_phone,
    get_miniprogram_open_id,
    get_file_verify_content,
)

from maneu.service import (
    # 常量（单一来源，勿在本地重复定义）
    SMS_CODE_PREFIX,
    # 用户
    get_guest_by_phone,
    get_or_create_guest_by_phone, get_or_create_guest_by_wechat,
    # 详情
    get_admin_by_id, get_order_by_id, get_store_by_id,
    get_report_by_id, get_repair_by_id,
    # 列表
    get_orders_by_phone, get_reports_by_phone,
    get_stores_by_phone, get_repairs_by_phone,
    # 短信
    generate_sms_code, save_sms_code, verify_sms_code,
    is_sms_locked, record_sms_fail,
)

logger = logging.getLogger(__name__)

# 发送冷却（apis 特有，service 不涉及）
SMS_SEND_COOLDOWN = 60
SMS_SEND_PREFIX = 'sms:send:'


# ============================================================================
# 一、通用工具
# ============================================================================

def _parse_json(request):
    """请求体解析为 dict；解析失败或非对象一律返回 {}。"""
    try:
        data = json.loads(request.body or '{}')
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}


def _extract_param(request, key):
    """从请求体取单个参数；不存在返回 None。"""
    return _parse_json(request).get(key)


def _json_error(message, status_code=400):
    """统一错误响应。"""
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
    """用微信手机号 code 换手机号；token 失效时刷新一次并重试。"""
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
        'access_token': util_jwt.generate_access_token(user),
        'refresh_token': util_jwt.generate_refresh_token(user),
    }


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

    return JsonResponse({
        'status': True,
        'message': '请求成功',
        'content': {
            'time': data.get('time'),
            'data': _safe_json(data.get('content')),
        },
    })


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

    return JsonResponse({
        'status': True,
        'message': '请求成功',
        'content': {
            'time': data.get('time'),
            'data': _safe_json(data.get('content')),
        },
    })


@csrf_exempt
@require_http_methods(["POST"])
def report_verify(request):
    """
    报告扫码验证。请求 {"index_id": "<UUID>"}。

    ⚠️ 结构：content.data.od.sph / content.data.os.sph（嵌套对象），
       不是平铺的 od_sph / os_sph；扫码端需按新结构读取。
    """
    index_id = _extract_param(request, 'index_id')
    if not util_verify.is_uuid(index_id):
        return _json_error('请提交正确的参数')

    data = get_report_by_id(index_id)
    if not data:
        return _json_error('记录不存在')

    return JsonResponse({
        'status': True,
        'message': '请求成功',
        'content': {
            'time': data.get('time'),
            'data': _safe_json(data.get('content')),
        },
    })


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

    return JsonResponse({
        'status': True,
        'message': '请求成功',
        'content': {
            'time': data.get('time'),
            'data': _safe_json(data.get('content')),
        },
    })


# ============================================================================
# 三、列表（需登录，路径含 /auth/）
# 手机号由 UserMiddleware 注入；可选 offset / limit 分页。
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def order_list(request):
    """当前用户订单列表；可选 {"offset": 0, "limit": 20}。"""
    phone = util_jwt.get_admin_phone_from_request(request)
    offset, limit = _paging_params(request)
    data = get_orders_by_phone(phone, offset, limit)
    return JsonResponse({'status': True, 'message': '请求成功', 'content': data})


@csrf_exempt
@require_http_methods(["POST"])
def report_list(request):
    """当前用户报告列表；可选 {"offset": 0, "limit": 20}。"""
    phone = util_jwt.get_admin_phone_from_request(request)
    offset, limit = _paging_params(request)
    data = get_reports_by_phone(phone, offset, limit)
    return JsonResponse({'status': True, 'message': '请求成功', 'content': data})


@csrf_exempt
@require_http_methods(["POST"])
def store_list(request):
    """当前用户门店列表；可选 {"offset": 0, "limit": 20}。"""
    phone = util_jwt.get_admin_phone_from_request(request)
    offset, limit = _paging_params(request)
    data = get_stores_by_phone(phone, offset, limit)
    return JsonResponse({'status': True, 'message': '请求成功', 'content': data})


@csrf_exempt
@require_http_methods(["POST"])
def repair_list(request):
    """当前用户维修记录列表；可选 {"offset": 0, "limit": 20}。"""
    phone = util_jwt.get_admin_phone_from_request(request)
    offset, limit = _paging_params(request)
    data = get_repairs_by_phone(phone, offset, limit)
    return JsonResponse({'status': True, 'message': '请求成功', 'content': data})


# ============================================================================
# 四、详情（需登录，路径含 /auth/）
# 需校验记录归属，仅允许访问本人记录。
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def guest_detail(request):
    """
    当前登录用户信息。
    身份由 UserMiddleware 注入的 jwt_phone 决定，不接收 code。
    """
    phone = util_jwt.get_admin_phone_from_request(request)
    if not phone:
        return _json_error('未登录', status_code=401)

    user = get_guest_by_phone(phone)
    if not user:
        return _json_error('用户不存在', status_code=404)

    return JsonResponse({
        'status': True,
        'message': '请求成功',
        'content': {
            'id': user.id,
            'open_id': user.open_id,
            'phone': user.phone,
            'name': user.name,
            'status': user.status,
            'remark': user.remark,
            'time': user.time,
        },
    })


@csrf_exempt
@require_http_methods(["POST"])
def guest_update(request):
    """
    更新当前登录用户昵称（预留：后续可扩展头像等字段）。
    请求 {"name": "..."}（可选）。
    """
    phone = util_jwt.get_admin_phone_from_request(request)
    if not phone:
        return _json_error('未登录', status_code=401)

    user = get_guest_by_phone(phone)
    if not user:
        return _json_error('用户不存在', status_code=404)

    data = _parse_json(request)
    update_fields = []

    if 'name' in data:
        name = str(data['name']).strip()
        if len(name) > 32:
            return _json_error('昵称过长')
        user.name = name
        update_fields.append('name')

    if not update_fields:
        return _json_error('没有可更新的字段')

    user.save(update_fields=update_fields)
    return JsonResponse({'status': True, 'message': '更新成功', 'content': {}})


@csrf_exempt
@require_http_methods(["POST"])
def order_detail(request):
    """订单详情。请求 {"code": "<UUID>"}。"""
    record_id = _extract_param(request, 'code')
    if not util_verify.is_uuid(record_id):
        return _json_error('记录ID无效')

    data = get_order_by_id(record_id)
    if not data:
        return _json_error('记录不存在', status_code=404)

    err = _check_owner(request, data)
    if err:
        return err

    admin = get_admin_by_id(data.get('admin_id')) or {}
    return JsonResponse({
        'status': True,
        'message': '请求成功',
        'content': {
            'time': data.get('time'),
            'name': data.get('name'),
            'phone': data.get('phone'),
            'remark': data.get('remark'),
            'content': data.get('content'),
            'admin_name': admin.get('nickname'),
            'admin_phone': admin.get('phone'),
            'admin_location': admin.get('location'),
            'admin_content': admin.get('content'),
        },
    })


@csrf_exempt
@require_http_methods(["POST"])
def store_detail(request):
    """门店详情。请求 {"code": "<UUID>"}。"""
    record_id = _extract_param(request, 'code')
    if not util_verify.is_uuid(record_id):
        return _json_error('记录ID无效')

    data = get_store_by_id(record_id)
    if not data:
        return _json_error('记录不存在', status_code=404)

    err = _check_owner(request, data)
    if err:
        return err

    admin = get_admin_by_id(data.get('admin_id')) or {}
    return JsonResponse({
        'status': True,
        'message': '请求成功',
        'content': {
            'time': data.get('time'),
            'name': data.get('name'),
            'phone': data.get('phone'),
            'remark': data.get('remark'),
            'content': data.get('content'),
            'admin_name': admin.get('nickname'),
            'admin_phone': admin.get('phone'),
            'admin_location': admin.get('location'),
            'admin_content': admin.get('content'),
        },
    })


@csrf_exempt
@require_http_methods(["POST"])
def report_detail(request):
    """报告详情。请求 {"code": "<UUID>"}。"""
    record_id = _extract_param(request, 'code')
    if not util_verify.is_uuid(record_id):
        return _json_error('记录ID无效')

    data = get_report_by_id(record_id)
    if not data:
        return _json_error('记录不存在', status_code=404)

    err = _check_owner(request, data)
    if err:
        return err

    admin = get_admin_by_id(data.get('admin_id')) or {}
    return JsonResponse({
        'status': True,
        'message': '请求成功',
        'content': {
            'time': data.get('time'),
            'name': data.get('name'),
            'phone': data.get('phone'),
            'remark': data.get('remark'),
            'content': data.get('content'),
            'admin_name': admin.get('nickname'),
            'admin_phone': admin.get('phone'),
            'admin_location': admin.get('location'),
            'admin_content': admin.get('content'),
        },
    })


@csrf_exempt
@require_http_methods(["POST"])
def repair_detail(request):
    """维修记录详情。请求 {"code": "<UUID>"}。"""
    record_id = _extract_param(request, 'code')
    if not util_verify.is_uuid(record_id):
        return _json_error('记录ID无效')

    data = get_repair_by_id(record_id)
    if not data:
        return _json_error('记录不存在', status_code=404)

    err = _check_owner(request, data)
    if err:
        return err

    admin = get_admin_by_id(data.get('admin_id')) or {}
    return JsonResponse({
        'status': True,
        'message': '请求成功',
        'content': {
            'time': data.get('time'),
            'name': data.get('name'),
            'phone': data.get('phone'),
            'remark': data.get('remark'),
            'content': data.get('content'),
            'admin_name': admin.get('nickname'),
            'admin_phone': admin.get('phone'),
            'admin_location': admin.get('location'),
            'admin_content': admin.get('content'),
        },
    })


# ============================================================================
# 五、认证（免登录）
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def send_sms(request):
    """
    发送短信验证码。请求 {"call": "手机号"}。
    ⚠️ 登录即注册：不再校验手机号是否已注册。
    """
    call = _extract_param(request, 'call')

    if not util_verify.is_call(call):
        return _json_error('请输入正确的手机号')

    cooldown_key = f'{SMS_SEND_PREFIX}{call}'
    if cache.get(cooldown_key):
        return _json_error('发送过于频繁，请稍后再试')
    cache.set(cooldown_key, 1, timeout=SMS_SEND_COOLDOWN)

    code = generate_sms_code()
    save_sms_code(call, code)

    ok, msg = _send_verification_code(call, code)
    if not ok:
        cache.delete(f'{SMS_CODE_PREFIX}{call}')
        cache.delete(cooldown_key)
        return _json_error(msg)

    return JsonResponse({'status': True, 'message': msg, 'content': {}})

@csrf_exempt
@require_http_methods(["POST"])
def login_by_sms(request):
    """
    短信登录；手机号未注册时自动创建账号。
    请求 {"call": "手机号", "code": "6位数字", "login_code": "<wx.login code>"}。
    login_code 可选：传了才尝试换 open_id 并绑定，换不到不阻断登录。
    """
    params = _parse_json(request)
    call = params.get('call')
    code = params.get('code')
    login_code = params.get('login_code')

    if not util_verify.is_call(call):
        return _json_error('请输入正确的手机号')
    if not util_verify.is_token_6(code):
        return _json_error('验证码格式错误')
    if is_sms_locked(call):
        return _json_error('验证码错误次数过多，请重新获取')
    if not verify_sms_code(call, code):
        record_sms_fail(call)
        return _json_error('验证码错误或已过期')

    # open_id 可选：拿不到不影响登录
    open_id = None
    if login_code:
        open_id = get_miniprogram_open_id(login_code)
        if not open_id:
            logger.warning('login_by_sms 获取 open_id 失败，降级为纯手机号登录')

    user, created = get_or_create_guest_by_wechat(open_id, call)

    return JsonResponse({
        'status': True,
        'message': '注册并登录成功' if created else '登录成功',
        'is_new': created,
        'call': user.phone,
        'content': {
            **_generate_jwt_for_user(user),
            'open_id': user.open_id,
        },
    })


@csrf_exempt
@require_http_methods(["POST"])
def login_by_wechat(request):
    """
    微信登录；首次登录自动创建账号。
    请求 {"code": "<手机号 code>", "login_code": "<wx.login code>"}。

    login_code 可选：传了才尝试换 open_id 并绑定，换不到按纯手机号登录。
    手机号 code 是核心，必须提供且格式合法。
    """
    phone_code = _extract_param(request, 'code')
    login_code = _extract_param(request, 'login_code')

    if not phone_code or not util_verify.is_token_64(phone_code):
        return _json_error('登录失败：请提交正确的微信号')

    # open_id 可选：换不到不阻断
    open_id = None
    if login_code:
        open_id = get_miniprogram_open_id(login_code)
        if not open_id:
            logger.warning('login_by_wechat 获取 open_id 失败，降级为纯手机号登录')

    token_data = get_miniprogram_token()
    access_token = token_data.get('access_token')
    if not access_token:
        return _json_error('系统错误，无法获取微信授权')

    phone = _fetch_phone_with_retry(phone_code, access_token)
    if phone is None:
        return _json_error('获取手机号失败，请联系管理员')

    user, created = get_or_create_guest_by_wechat(open_id, phone)

    return JsonResponse({
        'status': True,
        'message': '注册并登录成功' if created else '登录成功',
        'is_new': created,
        'call': user.phone,
        'content': {
            **_generate_jwt_for_user(user),
            'open_id': user.open_id,   # 可能为 None，前端存缓存时注意判空
        },
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

    user = get_guest_by_phone(user_phone)
    if not user:
        return _json_error('用户不存在', status_code=401)

    return JsonResponse({
        'status': True,
        'message': '刷新成功',
        'content': {
            'access_token': util_jwt.generate_access_token(user),
            'refresh_token': util_jwt.generate_refresh_token(user),
        },
    })


# ============================================================================
# 六、平台校验文件（微信小程序域名校验）
# ============================================================================

def VQwxjTJTH5(request):
    """微信域名校验文件，返回纯文本；内容需与小程序后台一致。"""
    return HttpResponse(
        get_file_verify_content(),
        content_type='text/plain',
    )