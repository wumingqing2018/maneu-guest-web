# -*- coding: utf-8 -*-
"""
API 接口模块 (重构版)
所有视图均为 JSON API 端点，仅接受 POST 请求。
响应统一格式：{"status": bool, "message": str, "content": any}
数据访问全部通过 service 层，视图层不再直接操作 Model。
"""

import json
import logging
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from common import util_common, util_verify, utli_jwt
from common.sendSMSForm import SendSMSForm
from common.userLoginForm import UserLoginForm

from maneu.service import *

logger = logging.getLogger(__name__)


# ========================= 内部辅助函数 =========================
# 注意：以下函数仅做通用工具，不再包含任何 Model 查询逻辑。

def _extract_param(request, key):
    """从请求中提取参数（支持 form 和 json）"""
    if request.content_type == 'application/json':
        try:
            return json.loads(request.body).get(key)
        except Exception:
            return None
    return request.POST.get(key)


def _json_error(message, status_code=400):
    """统一错误响应格式"""
    return JsonResponse({
        'status': False,
        'message': message,
        'content': {}
    }, status=status_code)


def _get_valid_access_token():
    """从缓存获取微信 access_token，若无效则自动刷新"""
    token = cache.get('wechat_access_token')
    if token:
        return token
    return _refresh_wechat_access_token()


def _refresh_wechat_access_token():
    """调用微信接口刷新 access_token，并写入缓存"""
    try:
        result = util_common.get_miniprogram_token()
        new_token = result.get('access_token') if result else None
        if new_token:
            cache.set('wechat_access_token', new_token, timeout=7000)
            return new_token
        logger.error('刷新微信 token 失败: %s', result)
        return None
    except Exception as e:
        logger.exception('刷新微信 token 异常: %s', e)
        return None


def _fetch_phone_with_retry(code, access_token):
    """获取手机号，失败时自动刷新 token 重试一次"""
    phone_info = util_common.get_miniprogram_phone(code, access_token)
    if phone_info.get('status'):
        return phone_info.get('message')

    logger.warning('微信 token 失效，尝试刷新...')
    new_token = _refresh_wechat_access_token()
    if not new_token:
        return None

    phone_info = util_common.get_miniprogram_phone(code, new_token)
    if phone_info.get('status'):
        return phone_info.get('message')

    logger.error('获取手机号最终失败: %s', phone_info.get('message'))
    return None


def _generate_jwt_for_user(user):
    """为用户生成 access_token 和 refresh_token"""
    return {
        'access_token': utli_jwt.generate_access_token(user),
        'refresh_token': utli_jwt.generate_refresh_token(user)
    }


def _send_verification_code(call, code):
    """发送短信验证码，返回 (success, message)"""
    try:
        response = util_common.send_sms_code(call=call, code=code)
        if response.get('status'):
            return True, '验证码已发送'
        return False, response.get('message', '发送失败')
    except Exception as e:
        logger.exception('发送短信异常: %s', e)
        return False, '系统繁忙，请稍后重试'


# ========================= API：验证接口 =========================

@csrf_exempt
@require_http_methods(["POST"])
def order_verify(request):
    """API：订单验证（根据 index_id 获取订单信息）"""
    index_id = _extract_param(request, 'index_id')
    if not util_verify.is_uuid(index_id):
        return _json_error('请提交正确的参数')

    data = get_order_by_id(index_id)
    if not data:
        return _json_error('记录不存在')

    content = {
        'time': data.get('time'),
        'data': json.loads(data.get('content', '{}'))
    }
    return JsonResponse({'status': True, 'message': '请求成功', 'content': content})


@csrf_exempt
@require_http_methods(["POST"])
def store_verify(request):
    """API：门店验证"""
    index_id = _extract_param(request, 'index_id')
    if not util_verify.is_uuid(index_id):
        return _json_error('请提交正确的参数')

    data = get_store_by_id(index_id)
    if not data:
        return _json_error('记录不存在')

    content = {
        'time': data.get('time'),
        'data': json.loads(data.get('content', '{}'))
    }
    return JsonResponse({'status': True, 'message': '请求成功', 'content': content})


@csrf_exempt
@require_http_methods(["POST"])
def report_verify(request):
    """API：报告验证"""
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


# ========================= API：列表接口 =========================

@csrf_exempt
@require_http_methods(["POST"])
def order_list(request):
    """API：当前用户的订单列表（status=3）"""
    phone = utli_jwt.get_admin_phone_from_request(request)
    data = get_orders_by_phone(phone, status=3)
    return JsonResponse({'status': True, 'message': '请求成功', 'content': data})


@csrf_exempt
@require_http_methods(["POST"])
def report_list(request):
    """API：当前用户的报告列表（status=2）"""
    phone = utli_jwt.get_admin_phone_from_request(request)
    data = get_reports_by_phone(phone, status=2)
    return JsonResponse({'status': True, 'message': '请求成功', 'content': data})


@csrf_exempt
@require_http_methods(["POST"])
def store_list(request):
    """API：当前用户的门店列表"""
    phone = utli_jwt.get_admin_phone_from_request(request)
    data = get_stores_by_phone(phone)
    return JsonResponse({'status': True, 'message': '请求成功', 'content': data})


@csrf_exempt
@require_http_methods(["POST"])
def repair_list(request):
    """API：当前用户的维修记录列表"""
    phone = utli_jwt.get_admin_phone_from_request(request)
    data = get_repairs_by_phone(phone)
    return JsonResponse({'status': True, 'message': '请求成功', 'content': data})


# ========================= API：详情接口 =========================

@csrf_exempt
@require_http_methods(["POST"])
def order_detail(request):
    """API：订单详情"""
    record_id = _extract_param(request, 'code')
    if not util_verify.is_uuid(record_id):
        return _json_error('记录ID无效')
    data = get_order_by_id(record_id)
    if not data:
        return _json_error('记录不存在', status_code=404)
    return JsonResponse({'status': True, 'message': '请求成功', 'content': data})


@csrf_exempt
@require_http_methods(["POST"])
def store_detail(request):
    """API：门店详情"""
    record_id = _extract_param(request, 'code')
    if not util_verify.is_uuid(record_id):
        return _json_error('记录ID无效')
    data = get_store_by_id(record_id)
    if not data:
        return _json_error('记录不存在', status_code=404)
    return JsonResponse({'status': True, 'message': '请求成功', 'content': data})


@csrf_exempt
@require_http_methods(["POST"])
def report_detail(request):
    """API：报告详情"""
    record_id = _extract_param(request, 'code')
    if not util_verify.is_uuid(record_id):
        return _json_error('记录ID无效')
    data = get_report_by_id(record_id)
    if not data:
        return _json_error('记录不存在', status_code=404)
    return JsonResponse({'status': True, 'message': '请求成功', 'content': data})


@csrf_exempt
@require_http_methods(["POST"])
def repair_detail(request):
    """API：维修记录详情"""
    record_id = _extract_param(request, 'code')
    if not util_verify.is_uuid(record_id):
        return _json_error('记录ID无效')
    data = get_repair_by_id(record_id)
    if not data:
        return _json_error('记录不存在', status_code=404)
    return JsonResponse({'status': True, 'message': '请求成功', 'content': data})


@csrf_exempt
@require_http_methods(["POST"])
def guest_detail(request):
    """API：当前登录用户信息"""
    phone = utli_jwt.get_admin_phone_from_request(request)
    user = get_guest_by_phone(phone)    # 返回 ManeuGuest 实例或 None
    if not user:
        return _json_error('用户不存在', status_code=404)

    return JsonResponse({
        'status': True,
        'message': '请求成功',
        'content': user
    })


# ========================= API：认证接口 =========================

@csrf_exempt
@require_http_methods(["POST"])
def sendsms(request):
    """API：发送短信验证码"""
    form = SendSMSForm(request.POST)
    if not form.is_valid():
        return _json_error(form.errors.as_text())

    call = form.cleaned_data['call']
    code = form.cleaned_data['code']
    ok, msg = _send_verification_code(call, code)
    if ok:
        return JsonResponse({'status': True, 'message': msg, 'content': {}})
    return _json_error(msg)


@csrf_exempt
@require_http_methods(["POST"])
def access_token_sms(request):
    """API：短信验证码登录"""
    form = UserLoginForm(request.POST)
    if not form.is_valid():
        return _json_error(form.errors.as_text())

    user = form.cleaned_data['user']    # 此时 user 应为 ManeuGuest 实例
    tokens = _generate_jwt_for_user(user)
    return JsonResponse({
        'status': True,
        'message': '登录成功',
        'content': tokens
    })


@csrf_exempt
@require_http_methods(["POST"])
def access_token_weixin(request):
    """API：微信小程序登录"""
    try:
        code = json.loads(request.body).get('code')
    except Exception:
        return _json_error('无效的JSON格式')

    if not code or not util_verify.is_token_64(code):
        return _json_error('登录失败：请提交正确的微信号')

    access_token = _get_valid_access_token()
    if not access_token:
        return _json_error('系统错误，无法获取微信授权')

    phone = _fetch_phone_with_retry(code, access_token)
    if phone is None:
        return _json_error('获取手机号失败，请联系管理员')

    # 使用 service 层获取用户
    user = get_guest_by_phone(phone)
    if not user:
        return _json_error('该手机号未注册')

    tokens = _generate_jwt_for_user(user)
    return JsonResponse({
        'status': True,
        'message': '登录成功',
        'content': tokens
    })


@csrf_exempt
@require_http_methods(["POST"])
def refresh_token(request):
    """API：刷新 access_token"""
    refresh_token = request.POST.get('refresh_token')
    if not refresh_token:
        return _json_error('缺少 refresh_token', status_code=401)

    payload = utli_jwt.verify_token(refresh_token, expected_type='refresh')
    if not payload:
        return _json_error('refresh_token 无效或已过期', status_code=401)

    user_phone = payload.get('user_phone')
    if not user_phone:
        return _json_error('请提交手机号', status_code=401)

    user = get_guest_by_phone(user_phone)
    if not user:
        return _json_error('用户不存在', status_code=401)

    new_access_token = utli_jwt.generate_access_token(user)
    return JsonResponse({
        'status': True,
        'message': '刷新成功',
        'content': {'access_token': new_access_token}
    })



def get_index(request):
    data = [{
        "index": 'https://maneu.online/static/img/3.gif',
        "data": 'https://maneu.online/static/img/gif2.jpg',
    }, {
        "index": 'https://maneu.online/static/img/1mcjs.jpg',
        "data": 'https://maneu.online/static/img/2mcjs.jpg',
    }, {
        "index": 'https://maneu.online/static/img/1xzy.jpg',
        "data": 'https://maneu.online/static/img/2xzy.jpg',
    }, {
        "index": 'https://maneu.online/static/img/1yqs.jpg',
        "data": 'https://maneu.online/static/img/2yqs.jpg',
    }, {
        "index": 'https://maneu.online/static/img/1njj.jpg',
        "data": 'https://maneu.online/static/img/2njj.jpg',
    }]
    return JsonResponse({'status': True, 'message': '', 'content': data})

