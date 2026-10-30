"""
maneu/apis.py

API 视图层
所有视图均为 JSON API 端点，仅处理请求参数与响应组装，不直接操作 Model。

职责：
    1. 接收并校验请求参数
    2. 调用 service 层获取 / 操作数据
    3. 组装统一格式的 JSON 响应

约定：
    1. 所有接口统一使用 JSON 请求体（Content-Type: application/json）
    2. 响应格式：{"status": bool, "message": str, "content": any}
    3. 错误响应由 _json_error() 构造，默认 HTTP 400
    4. 数据访问全部通过 maneu.service 层
    5. 需登录接口路径含 '/auth/'，由 UserMiddleware 自动拦截
    6. 需登录的详情接口额外校验记录归属（phone 必须匹配当前登录用户）

命名规则：
    - 扫码验证类：xxx_verify      （免登录）
    - 列表类：xxx_list            （需登录）
    - 详情类：xxx_detail          （需登录）
    - 认证类：send_sms / login_by_xxx / refresh_access_token
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
    # 数据查询
    get_admin_by_id,
    get_order_by_id,
    get_store_by_id,
    get_report_by_id,
    get_repair_by_id,
    get_orders_by_phone,
    get_reports_by_phone,
    get_stores_by_phone,
    get_repairs_by_phone,
    get_guest_by_phone,
    get_guest_model_by_phone,
    # 验证码
    generate_sms_code,
    save_sms_code,
    verify_sms_code,
    is_sms_locked,
    record_sms_fail,
)

logger = logging.getLogger(__name__)

# 短信发送冷却时间（秒），同一手机号在此期间内重复请求将被拒绝
SMS_SEND_COOLDOWN = 60
SMS_SEND_PREFIX = 'sms:send:'


# ============================================================================
# 一、内部辅助函数
# ============================================================================

def _parse_json(request):
    """
    解析请求体为 JSON dict。

    所有 API 统一使用 JSON 请求体（Content-Type: application/json）。
    解析失败或非对象类型时返回空 dict，由调用方自行判断。

    :param request: Django HTTP 请求
    :type request: HttpRequest
    :return: 参数字典，解析失败返回 {}
    :rtype: dict
    """
    try:
        data = json.loads(request.body or '{}')
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}


def _extract_param(request, key):
    """
    从 JSON 请求体中提取单个参数。

    :param request: Django HTTP 请求
    :type request: HttpRequest
    :param key: 参数名
    :type key: str
    :return: 参数值，不存在返回 None
    :rtype: str or None
    """
    return _parse_json(request).get(key)


def _json_error(message, status_code=400):
    """
    构造统一格式的错误响应。

    :param message: 错误提示
    :type message: str
    :param status_code: HTTP 状态码，默认 400
    :type status_code: int
    :return: JSON 响应
    :rtype: JsonResponse
    """
    return JsonResponse(
        {'status': False, 'message': message, 'content': {}},
        status=status_code,
    )


def _safe_json(raw, default=None):
    """
    安全解析 JSON 字符串；若已是 dict/list 直接返回，脏数据返回 default。

    用于 content 字段可能是 TextField（字符串）或 JSONField（已是对象）的场景。

    :param raw: 原始 content 值
    :param default: 解析失败时的兜底值，默认 {}
    :return: dict / list / default
    """
    if isinstance(raw, (dict, list)):
        return raw
    try:
        return json.loads(raw or '{}')
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else {}


def _check_owner(request, data):
    """
    校验记录归属：记录的 phone 必须与当前登录用户一致。

    历史数据 phone 为空时放行（避免旧记录全部不可访问）。

    :param request: Django HTTP 请求（已通过 UserMiddleware 注入 jwt_phone）
    :param data: 记录 dict
    :return: 通过返回 None，不通过返回错误响应
    :rtype: JsonResponse or None
    """
    record_phone = data.get('phone')
    if not record_phone:
        return None

    phone = util_jwt.get_admin_phone_from_request(request)
    if record_phone != phone:
        return _json_error('无权访问该记录', status_code=403)
    return None


def _fetch_phone_with_retry(code, access_token):
    """
    获取微信手机号；token 失效时自动刷新并重试一次。

    :param code: wx.login 返回的临时凭证
    :type code: str
    :param access_token: 微信接口调用凭据
    :type access_token: str
    :return: 手机号字符串，失败返回 None
    :rtype: str or None
    """
    phone_info = get_miniprogram_phone(code, access_token)
    if phone_info.get('status'):
        return phone_info.get('message')

    logger.warning('微信 token 失效，尝试刷新...')
    token_data = get_miniprogram_token(force_refresh=True)
    new_token = token_data.get('access_token')
    if not new_token:
        return None

    phone_info = get_miniprogram_phone(code, new_token)
    if phone_info.get('status'):
        return phone_info.get('message')

    logger.error('获取手机号最终失败: %s', phone_info.get('message'))
    return None


def _generate_jwt_for_user(user):
    """
    为指定用户生成 JWT 令牌对。

    :param user: ManeuGuest ORM 实例（需有 id / phone 属性）
    :type user: ManeuGuest
    :return: {'access_token': str, 'refresh_token': str}
    :rtype: dict
    """
    return {
        'access_token': util_jwt.generate_access_token(user),
        'refresh_token': util_jwt.generate_refresh_token(user),
    }


def _send_verification_code(call, code):
    """
    发送短信验证码。

    :param call: 手机号
    :type call: str
    :param code: 6 位验证码
    :type code: str
    :return: (success: bool, message: str)
    :rtype: tuple
    """
    try:
        response = send_sms_code(call=call, code=code)
        if response.get('status'):
            return True, '验证码已发送'
        return False, response.get('message', '发送失败')
    except Exception as e:
        logger.exception('发送短信异常: %s', e)
        return False, '系统繁忙，请稍后重试'


def _paging_params(request):
    """
    从请求体提取分页参数，非法值归一为 None（表示不分页）。

    :param request: Django HTTP 请求
    :return: (offset, limit)
    :rtype: tuple[int or None, int or None]
    """
    params = _parse_json(request)

    def _to_int(v):
        try:
            i = int(v)
            return i if i >= 0 else None
        except (TypeError, ValueError):
            return None

    return _to_int(params.get('offset')), _to_int(params.get('limit'))


# ============================================================================
# 二、扫码验证类接口（免登录）
# 用途：用户扫二维码后，根据 index_id 返回对应记录信息
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def order_verify(request):
    """
    API：订单验证
    根据 index_id 返回订单信息。

    请求体（JSON）：
        {"index_id": "<订单 UUID>"}
    """
    index_id = _extract_param(request, 'index_id')
    if not util_verify.is_uuid(index_id):
        return _json_error('请提交正确的参数')

    data = get_order_by_id(index_id)
    if not data:
        return _json_error('记录不存在')

    content = {
        'time': data.get('time'),
        'data': _safe_json(data.get('content')),
    }
    return JsonResponse({'status': True, 'message': '请求成功', 'content': content})


@csrf_exempt
@require_http_methods(["POST"])
def store_verify(request):
    """
    API：门店验证
    根据 index_id 返回门店信息。

    请求体（JSON）：
        {"index_id": "<门店 UUID>"}
    """
    index_id = _extract_param(request, 'index_id')
    if not util_verify.is_uuid(index_id):
        return _json_error('请提交正确的参数')

    data = get_store_by_id(index_id)
    if not data:
        return _json_error('记录不存在')

    content = {
        'time': data.get('time'),
        'data': _safe_json(data.get('content')),
    }
    return JsonResponse({'status': True, 'message': '请求成功', 'content': content})


@csrf_exempt
@require_http_methods(["POST"])
def report_verify(request):
    """
    API：报告验证
    根据 index_id 返回报告信息。

    请求体（JSON）：
        {"index_id": "<报告 UUID>"}
    """
    index_id = _extract_param(request, 'index_id')
    if not util_verify.is_uuid(index_id):
        return _json_error('请提交正确的参数')

    data = get_report_by_id(index_id)
    if not data:
        return _json_error('记录不存在')

    fields = ['time', 'plan', 'os_va', 'os_cyl', 'os_sph', 'os_ax',
              'od_va', 'od_cyl', 'od_sph', 'od_ax']
    content = {f: data.get(f) for f in fields}
    return JsonResponse({'status': True, 'message': '请求成功', 'content': content})


@csrf_exempt
@require_http_methods(["POST"])
def repair_verify(request):
    """
    API：维修记录验证
    根据 index_id 返回维修记录信息。

    请求体（JSON）：
        {"index_id": "<维修记录 UUID>"}
    """
    index_id = _extract_param(request, 'index_id')
    if not util_verify.is_uuid(index_id):
        return _json_error('请提交正确的参数')

    data = get_repair_by_id(index_id)
    if not data:
        return _json_error('记录不存在')

    content = {
        'time': data.get('time'),
        'data': _safe_json(data.get('content')),
    }
    return JsonResponse({'status': True, 'message': '请求成功', 'content': content})


# ============================================================================
# 三、列表类接口（需登录，路径含 /auth/）
# 用途：返回当前登录用户的各类记录列表
# 说明：手机号由 UserMiddleware 注入到 request.jwt_phone
#       支持可选 offset / limit 分页参数，不传则返回全量
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def order_list(request):
    """
    API：当前用户的订单列表

    请求体（JSON，可选分页）：
        {"offset": 0, "limit": 20}
    """
    phone = util_jwt.get_admin_phone_from_request(request)
    offset, limit = _paging_params(request)
    data = get_orders_by_phone(phone, offset=offset, limit=limit)
    return JsonResponse({'status': True, 'message': '请求成功', 'content': data})


@csrf_exempt
@require_http_methods(["POST"])
def report_list(request):
    """
    API：当前用户的报告列表

    请求体（JSON，可选分页）：
        {"offset": 0, "limit": 20}
    """
    phone = util_jwt.get_admin_phone_from_request(request)
    offset, limit = _paging_params(request)
    data = get_reports_by_phone(phone, offset=offset, limit=limit)
    return JsonResponse({'status': True, 'message': '请求成功', 'content': data})


@csrf_exempt
@require_http_methods(["POST"])
def store_list(request):
    """
    API：当前用户的门店列表

    请求体（JSON，可选分页）：
        {"offset": 0, "limit": 20}
    """
    phone = util_jwt.get_admin_phone_from_request(request)
    offset, limit = _paging_params(request)
    data = get_stores_by_phone(phone, offset=offset, limit=limit)
    return JsonResponse({'status': True, 'message': '请求成功', 'content': data})


@csrf_exempt
@require_http_methods(["POST"])
def repair_list(request):
    """
    API：当前用户的维修记录列表

    请求体（JSON，可选分页）：
        {"offset": 0, "limit": 20}
    """
    phone = util_jwt.get_admin_phone_from_request(request)
    offset, limit = _paging_params(request)
    data = get_repairs_by_phone(phone, offset=offset, limit=limit)
    return JsonResponse({'status': True, 'message': '请求成功', 'content': data})


# ============================================================================
# 四、详情类接口（需登录，路径含 /auth/）
# 用途：根据记录 ID 返回详情
# 安全：额外校验记录归属，仅允许访问本人记录
# 说明：admin 字段暂置于响应顶层以兼容小程序，后续可考虑并入 content
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def order_detail(request):
    """
    API：订单详情

    请求体（JSON）：
        {"code": "<订单 UUID>"}
    """
    record_id = _extract_param(request, 'code')
    if not util_verify.is_uuid(record_id):
        return _json_error('记录ID无效')

    data = get_order_by_id(record_id)
    if not data:
        return _json_error('记录不存在', status_code=404)

    err = _check_owner(request, data)
    if err:
        return err

    admin = get_admin_by_id(admin_id=data.get('admin_id'))
    return JsonResponse({'status': True, 'message': '请求成功', 'content': data, 'admin': admin})


@csrf_exempt
@require_http_methods(["POST"])
def store_detail(request):
    """
    API：门店详情

    请求体（JSON）：
        {"code": "<门店 UUID>"}
    """
    record_id = _extract_param(request, 'code')
    if not util_verify.is_uuid(record_id):
        return _json_error('记录ID无效')

    data = get_store_by_id(record_id)
    if not data:
        return _json_error('记录不存在', status_code=404)

    err = _check_owner(request, data)
    if err:
        return err

    admin = get_admin_by_id(admin_id=data.get('admin_id'))
    return JsonResponse({'status': True, 'message': '请求成功', 'content': data, 'admin': admin})


@csrf_exempt
@require_http_methods(["POST"])
def report_detail(request):
    """
    API：报告详情

    请求体（JSON）：
        {"code": "<报告 UUID>"}
    """
    record_id = _extract_param(request, 'code')
    if not util_verify.is_uuid(record_id):
        return _json_error('记录ID无效')

    data = get_report_by_id(record_id)
    if not data:
        return _json_error('记录不存在', status_code=404)

    err = _check_owner(request, data)
    if err:
        return err

    admin = get_admin_by_id(admin_id=data.get('admin_id'))
    return JsonResponse({'status': True, 'message': '请求成功', 'content': data, 'admin': admin})


@csrf_exempt
@require_http_methods(["POST"])
def repair_detail(request):
    """
    API：维修记录详情

    请求体（JSON）：
        {"code": "<维修记录 UUID>"}
    """
    record_id = _extract_param(request, 'code')
    if not util_verify.is_uuid(record_id):
        return _json_error('记录ID无效')

    data = get_repair_by_id(record_id)
    if not data:
        return _json_error('记录不存在', status_code=404)

    err = _check_owner(request, data)
    if err:
        return err

    admin = get_admin_by_id(admin_id=data.get('admin_id'))
    return JsonResponse({'status': True, 'message': '请求成功', 'content': data, 'admin': admin})


@csrf_exempt
@require_http_methods(["POST"])
def guest_detail(request):
    """
    API：当前登录用户信息
    手机号由 UserMiddleware 注入到 request.jwt_phone。

    请求体（JSON）：
        {}
    """
    phone = util_jwt.get_admin_phone_from_request(request)
    user = get_guest_by_phone(phone)
    if not user:
        return _json_error('用户不存在', status_code=404)
    return JsonResponse({'status': True, 'message': '请求成功', 'content': user})


# ============================================================================
# 五、认证类接口（免登录）
# 用途：短信发送、短信登录、微信登录、刷新 access_token
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def send_sms(request):
    """
    API：发送短信验证码

    请求体（JSON）：
        {"call": "13640651582"}

    流程：
        1. 校验手机号格式
        2. 确认手机号已注册
        3. 冷却检查（同一手机号 60 秒内只能发送一次）
        4. 生成验证码 → 存 Redis
        5. 调用阿里云发送（失败时清理验证码与冷却）
    """
    call = _extract_param(request, 'call')

    # 1. 手机号格式校验
    if not util_verify.is_call(call):
        return _json_error('请输入正确的手机号')

    # 2. 手机号必须已注册
    if not get_guest_model_by_phone(call):
        return _json_error('当前账号未注册')

    # 3. 冷却检查，防止短信轰炸
    cooldown_key = f'{SMS_SEND_PREFIX}{call}'
    if cache.get(cooldown_key):
        return _json_error('发送过于频繁，请稍后再试')
    cache.set(cooldown_key, 1, timeout=SMS_SEND_COOLDOWN)

    # 4. 生成验证码并存入 Redis
    code = generate_sms_code()
    save_sms_code(call, code)

    # 5. 发送短信，失败时回滚
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
    API：短信验证码登录

    请求体（JSON）：
        {"call": "13640651582", "code": "123456"}

    流程：
        1. 校验手机号、验证码格式
        2. 检查是否因错误次数过多被锁定
        3. 校验验证码（Redis，成功后自动删除）
        4. 查库拿用户，生成 JWT
    """
    params = _parse_json(request)
    call = params.get('call')
    code = params.get('code')

    # 1. 格式校验
    if not util_verify.is_call(call):
        return _json_error('请输入正确的手机号')
    if not util_verify.is_token_6(code):
        return _json_error('验证码格式错误')

    # 2. 防爆破：错误次数过多直接拒绝
    if is_sms_locked(call):
        return _json_error('验证码错误次数过多，请重新获取')

    # 3. 验证码校验（成功后自动从 Redis 删除）
    if not verify_sms_code(call, code):
        record_sms_fail(call)
        return _json_error('验证码错误或已过期')

    # 4. 查用户
    user = get_guest_model_by_phone(call)
    if not user:
        return _json_error('该手机号未注册')

    # 5. 生成 JWT
    tokens = _generate_jwt_for_user(user)
    return JsonResponse({'status': True, 'message': '登录成功', 'content': tokens})


@csrf_exempt
@require_http_methods(["POST"])
def login_by_wechat(request):
    """
    API：微信小程序登录

    请求体（JSON）：
        {"code": "<64位十六进制字符串>"}

    流程：
        1. 接收小程序 wx.login 返回的 code
        2. 用 code 换取手机号（token 失效时自动刷新重试）
        3. 查库拿用户，生成 JWT
    """
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

    # 必须用 ORM 实例（生成 JWT 需要 user.id / user.phone）
    user = get_guest_model_by_phone(phone)
    if not user:
        return _json_error('该手机号未注册')

    tokens = _generate_jwt_for_user(user)
    return JsonResponse({'status': True, 'message': '登录成功', 'content': tokens})


@csrf_exempt
@require_http_methods(["POST"])
def refresh_access_token(request):
    """
    API：刷新 access_token

    请求体（JSON）：
        {"refresh_token": "<上次登录返回的 refresh_token>"}

    用 refresh_token 换新的 access_token 与 refresh_token。
    ⚠️ refresh_token 采用轮换策略：每次刷新后旧 refresh_token 不再保证有效，
       客户端必须保存响应中的新 refresh_token。
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

    # 必须用 ORM 实例（生成 JWT 需要 user.id / user.phone）
    user = get_guest_model_by_phone(user_phone)
    if not user:
        return _json_error('用户不存在', status_code=401)

    new_access_token = util_jwt.generate_access_token(user)
    new_refresh_token = util_jwt.generate_refresh_token(user)
    return JsonResponse({
        'status': True,
        'message': '刷新成功',
        'content': {
            'access_token': new_access_token,
            'refresh_token': new_refresh_token,
        },
    })


# ============================================================================
# 六、平台校验文件（微信小程序服务器域名校验）
# ============================================================================

def VQwxjTJTH5(request):
    # 替换为校验文件中的真实内容
    from django.http import HttpResponse
    file_content = "c8966dfaa24aa981832913b888981534"
    return HttpResponse(file_content, content_type='text/plain')
