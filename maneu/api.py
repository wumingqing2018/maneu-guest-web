import json
import uuid

from common.forms.sendSMSForm import SendSMSForm
from common.forms.userLoginForm import UserLoginForm
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from common import common,verify
from common.utli_jwt import *
from maneu.service import *
from maneu.models import *


def order_verify(request):
    index_id = verify.is_uuid(request.GET.get('index_id'))
    if index_id:

        try:
            data = ManeuStore.objects.filter(id=index_id).first()
            data_time = data.time
            data_data = json.loads(data.content)
            content = {'status': True, 'message': '请求成功', 'content': {'time': data_time, 'data': data_data}}
        except Exception as e:
            content = {'status': 'false', 'message': str(e), 'content': {}, 'token': ''}


    else:
        content = {'status': 'false', 'message': '没有找到你的订单', 'content': {}, 'token': ''}
    return JsonResponse(content)


def store_verify(request):
    index_id = verify.is_uuid(request.GET.get('index_id'))
    if index_id:

        try:
            data = ManeuStore.objects.filter(id=index_id).first()
            data_time = data.time
            data_data = json.loads(data.content)
            content = {'status': True, 'message': '请求成功', 'content': {'time': data_time, 'data': data_data}}
        except Exception as e:
            content = {'status': False, 'message': str(e), 'content': {}, 'token': ''}

    else:
        content = {'status': False, 'message': '请提交正确的参数', 'content': {}, 'token': ''}
    return JsonResponse(content)


def report_verify(request):
    index_id = verify.is_uuid(request.GET.get('index_id'))
    if index_id:

        try:
            data = ManeuReport.objects.filter(id=index_id).first()
            content = {'status': True, 'message': '请求成功', 'content': {'time': data.time, 'plan': data.plan, 'os_va': data.os_va, 'os_cyl': data.os_cyl, 'os_sph': data.os_sph, 'os_ax': data.os_ax, 'od_va': data.od_va, 'od_cyl': data.od_cyl, 'od_sph': data.od_sph, 'od_ax': data.od_ax}}
        except Exception as e:
            content = {'status': False, 'message': str(e), 'content': {}, 'token': ''}


    else:
        content = {'status': False, 'message': '请提交正确的参数', 'content': {}, 'token': ''}
    return JsonResponse(content)


def login(request):
    call = verify.is_call(request.GET.get('call'))
    code = verify.is_token_6(request.GET.get('code'))

    if call and code:
        token = uuid.uuid4()
        guest = ManeuGuest.objects.filter(phone=call).all().update(remark=token)
        if guest:
            content = {'status': True, 'message': '请求成功', 'content': {}, 'token': token}
        else:
            content = {'status': False, 'message': '请求失败', 'content': {}, 'token': ''}
    else:
        content = {'status': False, 'message': '登录失败：请提交正确的手机号和验证码', 'content': {}, 'token': ''}

    return JsonResponse(content)


def login_wx(request):
    code = verify.is_token_64(request.GET.get('code'))
    if code:
        data_token = ManeuAdmin.objects.filter().first()
        phone = common.get_phone_number(code, data_token.content)
        if phone['status']:
            token = uuid.uuid4()
            guest = ManeuGuest.objects.filter(phone=phone['message']).update(remark=token)
            if guest != 0:
                content = {'status': True, 'message': '请求成功', 'content': {}, 'token': token}
            else:
                content = {'status': False, 'message': '请求失败', 'content': {}, 'token': ''}
        else:
            data_token = common.get_miniprogram_token()['access_token']
            ManeuAdmin.objects.all().update(content=data_token)
            phone = common.get_phone_number(code, data_token)
            if phone['status']:
                token = uuid.uuid4()
                guest = ManeuGuest.objects.filter(phone=phone['message']).update(remark=token)
                if guest != 0:
                    content = {'status': True, 'message': '请求成功', 'content': {}, 'token': token}
                else:
                    content = {'status': False, 'message': '请求失败', 'content': {}, 'token': ''}
            else:
                content = {'status': False, 'message': '请求失败：请联系管理员', 'content': {}, 'token': ''}
    else:
        content = {'status': False, 'message': '登录失败：请提交正确的微信号', 'content': {}, 'token': ''}

    return JsonResponse(content)


def sendsms(request):
    call = verify.is_call(request.GET.get('code'))
    if call:
        code = common.randint()
        data = ManeuGuest.objects.filter(phone=call).all().update(remark=code)
        if data:
            response = sendsms(call, code)
            if response['Code'] == 'OK':
                content = {'status': True, 'message': '请求成功', 'content': {}, 'token': ''}
            else:
                content = {'status': False, 'message': '短信发送失败，今日次数用完了', 'content': {}, 'token': ''}
        else:
            content = {'status': False, 'message': '请求失败', 'content': {}, 'token': ''}
    else:
        content = {'status': False, 'message': '登录失败：请提交正确的手机号', 'content': {}, 'token': ''}
    return JsonResponse(content)


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
    return JsonResponse({'status': True, 'message': '', 'content': data, 'token': ''})




# ---------- 列表类接口（返回多条记录） ----------

def order_list(request):
    """
    获取当前用户的订单列表（仅限状态为 3 的订单）
    请求方式：GET
    参数：
        token (str): 用户身份凭证（UUID）
    返回：
        {
            status: bool,       # 请求是否成功
            message: str,       # 提示信息
            content: list,      # 订单数据列表（每个元素为字典）
            token: str          # 新的 token（用于下一次请求）
        }
    流程：
        1. 验证 token 是否有效（UUID 格式）
        2. 通过 token 查询 ManeuGuest 表获取用户
        3. 若用户存在，则立即生成新 token 并更新到该用户的 remark 字段（实现 token 换发）
        4. 查询 ManeuOrder 表，按手机号筛选状态为 3 的订单，按时间倒序
        5. 返回数据和新 token
        6. 若用户不存在或 token 无效，返回错误并提示重新登录
    """
    token = verify.is_uuid(request.GET.get('token'))
    if token:
        # 生成新 token
        remark = str(uuid.uuid4())
        guest = ManeuGuest.objects.filter(remark=token).first()
        # 尝试更新用户的 remark 为新的 token，若返回值不为 0 表示更新成功（用户存在）
        if ManeuGuest.objects.filter(remark=token).update(remark=remark) != 0:
            # 查询订单：phone 匹配、status=3（已完成的订单），按 time 倒序
            data = ManeuOrder.objects.filter(phone=guest.phone, status=3) \
                                     .order_by('-time') \
                                     .all() \
                                     .values('id', 'name', 'time', 'phone', 'remark')
            return JsonResponse({
                'status': True,
                'message': '',
                'content': list(data),
                'token': remark
            })
        else:
            # 更新失败（说明 token 对应的用户不存在）
            content = {'status': False, 'message': '请重新登录', 'content': {}, 'token': ''}
    else:
        # token 格式无效
        content = {'status': False, 'message': '请重新登录', 'content': {}, 'token': ''}

    return JsonResponse(content)


def report_list(request):
    """
    获取当前用户的报告列表（仅限状态为 2 的报告）
    参数与返回格式同 order_list，区别在于查询 ManeuReport 表
    注意：此处先获取 guest 对象，再判断是否存在，与 order_list 略有不同，但逻辑等价
    """
    token = verify.is_uuid(request.GET.get('token'))
    guest = ManeuGuest.objects.filter(remark=token).first()
    if guest:
        remark = str(uuid.uuid4())
        # 更新 token
        guest_update = ManeuGuest.objects.filter(remark=token).update(remark=remark)
        # 查询报告：手机号匹配且 status=2
        data = ManeuReport.objects.filter(phone=guest.phone, status=2) \
                                  .order_by('-time') \
                                  .all() \
                                  .values('id', 'name', 'time', 'phone', 'remark')
        return JsonResponse({'status': True, 'message': '', 'content': list(data), 'token': remark})
    else:
        content = {'status': False, 'message': '请重新登录。', 'content': {}, 'token': ''}
    return JsonResponse(content)


def store_list(request):
    """
    获取当前用户的门店列表（无状态过滤，返回所有门店记录）
    参数与返回格式同 order_list，查询 ManeuStore 表
    """
    token = verify.is_uuid(request.GET.get('token'))
    guest = ManeuGuest.objects.filter(remark=token).first()
    if guest:
        remark = str(uuid.uuid4())
        guest_update = ManeuGuest.objects.filter(remark=token).update(remark=remark)
        data = ManeuStore.objects.filter(phone=guest.phone) \
                                 .order_by('-time') \
                                 .all() \
                                 .values('id', 'name', 'time', 'phone', 'remark')
        return JsonResponse({'status': True, 'message': '', 'content': list(data), 'token': remark})
    else:
        content = {'status': False, 'message': '请重新登录。', 'content': {}, 'token': ''}
    return JsonResponse(content)


def repair_list(request):
    """
    获取当前用户的维修记录列表（无状态过滤）
    参数与返回格式同 order_list，查询 ManeuRepair 表
    """
    token = verify.is_uuid(request.GET.get('token'))
    guest = ManeuGuest.objects.filter(remark=token).first()
    if guest:
        remark = str(uuid.uuid4())
        guest_update = ManeuGuest.objects.filter(remark=token).update(remark=remark)
        data = ManeuRepair.objects.filter(phone=guest.phone) \
                                  .order_by('-time') \
                                  .all() \
                                  .values('id', 'name', 'time', 'phone', 'remark')
        return JsonResponse({'status': True, 'message': '', 'content': list(data), 'token': remark})
    else:
        content = {'status': False, 'message': '请重新登录。', 'content': {}, 'token': ''}
    return JsonResponse(content)


# ---------- 详情类接口（返回单条记录） ----------

def order_detail(request):
    """
    获取指定订单的详细信息
    请求方式：GET
    参数：
        code (str): 订单 ID（UUID 格式）
        token (str): 用户凭证（UUID）
    返回：
        status: bool, message: str, content: dict（订单详情）, token: str
    流程：
        1. 验证 code 和 token 是否为合法 UUID
        2. 使用 token 更新用户 remark（换发新 token），若更新失败则用户无效
        3. 根据 code 查询订单，若存在则返回模型数据，否则捕获异常返回错误信息
    """
    code = verify.is_uuid(request.GET.get('code'))
    mark = verify.is_uuid(request.GET.get('token'))

    if code or mark:  # 注意：这里是 or，只要有一个有效即可（可能设计初衷允许 code 为空？但实际需要 code）
        remark = uuid.uuid4()  # 注意：此处生成的是 UUID 对象，后面直接用于字符串？实际上应转为 str
        # 更新用户的 token，若返回 0 表示未找到该用户
        guest = ManeuGuest.objects.filter(remark=mark).update(remark=remark)
        if guest != 0:
            try:
                data = ManeuOrder.objects.filter(id=code).first()
                # 使用 model_to_dict 将模型实例转为字典
                content = {'status': True, 'message': '请求成功', 'content': model_to_dict(data), 'token': remark}
            except Exception as e:
                content = {'status': False, 'message': str(e), 'content': {}, 'token': remark}
        else:
            content = {'status': False, 'message': '请重新登录', 'content': {}, 'token': ''}
    else:
        content = {'status': False, 'message': '请重新登录', 'content': {}, 'token': ''}

    return JsonResponse(content)


def store_detail(request):
    """
    获取指定门店的详细信息
    参数及逻辑同 order_detail，查询 ManeuStore 表
    """
    code = verify.is_uuid(request.GET.get('code'))
    mark = verify.is_uuid(request.GET.get('token'))

    if code or mark:
        remark = uuid.uuid4()
        guest = ManeuGuest.objects.filter(remark=mark).update(remark=remark)
        if guest != 0:
            try:
                data = ManeuStore.objects.filter(id=code).first()
                content = {'status': True, 'message': '请求成功', 'content': model_to_dict(data), 'token': remark}
            except Exception as e:
                content = {'status': False, 'message': str(e), 'content': {}, 'token': remark}
        else:
            content = {'status': False, 'message': '请重新登录', 'content': {}, 'token': ''}
    else:
        content = {'status': False, 'message': '请重新登录', 'content': {}, 'token': ''}

    return JsonResponse(content)


def guest_detail(request):
    """
    获取当前用户自己的详细信息
    参数：code 为用户 ID，token 为凭证
    逻辑同 order_detail，但查询 ManeuGuest 表
    """
    code = verify.is_uuid(request.GET.get('code'))
    mark = verify.is_uuid(request.GET.get('token'))

    if code or mark:
        remark = uuid.uuid4()
        guest = ManeuGuest.objects.filter(remark=mark).update(remark=remark)
        if guest != 0:
            try:
                data = ManeuGuest.objects.filter(id=code).first()
                content = {'status': True, 'message': '请求成功', 'content': model_to_dict(data), 'token': remark}
            except Exception as e:
                content = {'status': False, 'message': str(e), 'content': {}, 'token': remark}
        else:
            content = {'status': False, 'message': '请重新登录', 'content': {}, 'token': ''}
    else:
        content = {'status': False, 'message': '请重新登录', 'content': {}, 'token': ''}

    return JsonResponse(content)


def report_detail(request):
    """
    获取指定报告的详细信息
    参数及逻辑同 order_detail，查询 ManeuReport 表
    """
    code = verify.is_uuid(request.GET.get('code'))
    mark = verify.is_uuid(request.GET.get('token'))

    if code or mark:
        remark = uuid.uuid4()
        guest = ManeuGuest.objects.filter(remark=mark).update(remark=remark)
        if guest != 0:
            try:
                data = ManeuReport.objects.filter(id=code).first()
                content = {'status': True, 'message': '请求成功', 'content': model_to_dict(data), 'token': remark}
            except Exception as e:
                content = {'status': False, 'message': str(e), 'content': {}, 'token': remark}
        else:
            content = {'status': False, 'message': '请重新登录', 'content': {}, 'token': ''}
    else:
        content = {'status': False, 'message': '请重新登录', 'content': {}, 'token': ''}

    return JsonResponse(content)


def repair_detail(request):
    """
    获取指定维修记录的详细信息
    参数及逻辑同 order_detail，查询 ManeuRepair 表
    """
    code = verify.is_uuid(request.GET.get('code'))
    mark = verify.is_uuid(request.GET.get('token'))

    if code or mark:
        remark = uuid.uuid4()
        guest = ManeuGuest.objects.filter(remark=mark).update(remark=remark)
        if guest != 0:
            try:
                data = ManeuRepair.objects.filter(id=code).first()
                content = {'status': True, 'message': '请求成功', 'content': model_to_dict(data), 'token': remark}
            except Exception as e:
                content = {'status': False, 'message': str(e), 'content': {}, 'token': remark}
        else:
            content = {'status': False, 'message': '请重新登录', 'content': {}, 'token': ''}
    else:
        content = {'status': False, 'message': '请重新登录', 'content': {}, 'token': ''}

    return JsonResponse(content)


@csrf_exempt  # 因为使用 JWT，无需 CSRF
@require_http_methods(["POST"])  # 只允许 POST
def sendsms(request):
    form = SendSMSForm(request.POST)
    if form.is_valid():
        call = form.cleaned_data['call']
        code = form.cleaned_data['code']  # 由表单 clean 生成的验证码

        # 调用短信发送服务
        response = sendsms(call=call, code=code)
        if response.get('Code') == 'OK':
            content = {'status': True,'message': '验证码已发送', 'content': {}}
        else:
            content = {'status': False, 'message': response["Message"], 'content': {}}
    else:
        content = {'status': False, 'message': form.errors.as_text(), 'content': {}}
    return JsonResponse(content)



@csrf_exempt  # 因为使用 JWT，无需 CSRF
@require_http_methods(["POST"])  # 只允许 POST
def access_token_sms(request):
    form = UserLoginForm(request.POST)

    if form.is_valid():
        # 从表单获取已验证的用户对象（假设你在 form.clean() 中设置了 'user'）
        user = form.cleaned_data['user']
        a_token = generate_access_token(user)
        r_token = generate_refresh_token(user)
        content = {'status': True, 'message': '登录成功', 'content': {'access_token': a_token,'refresh_token': r_token}}
    else:
        content = {'status': False, 'message': form.errors.as_text(), 'content': {}}

    return JsonResponse(content)



@csrf_exempt  # 因为使用 JWT，无需 CSRF
@require_http_methods(["POST"])  # 只允许 POST
def refresh_token(request):
    """刷新 access token（接收 refresh_token，返回新 access_token）"""
    token = request.POST.get('refresh_token')
    if not token:
        return JsonResponse({'status': False, 'message': '缺少 refresh_token'}, status=401)

    payload = verify_token(token, expected_type='refresh')
    if not payload:
        return JsonResponse({'status': False, 'message': 'refresh_token 无效或已过期'}, status=401)

    user = admin_find_id(payload['user_id'])
    if not payload:
        return JsonResponse({'status': False, 'message': '用户不存在'}, status=401)

    new_access_token = generate_access_token(user)
    # 如需滚动刷新，可同时生成新的 refresh_token 返回
    # new_refresh_token = generate_refresh_token(user)
    return JsonResponse({
        'status': True,
        'access_token': new_access_token,
        # 'refresh_token': new_refresh_token,   # 若启用滚动刷新取消注释
    })


def remove_token(request):
    """前端清除 token 后跳转登录页，这里只做重定向"""
    content = {'status': True, 'message': 'OK', 'content': {}}
    return JsonResponse(content)
