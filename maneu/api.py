import json

from django.http import JsonResponse

from common import common
from common import verify_util
from maneu.models import *
from django.forms.models import model_to_dict
import uuid
from common.userLoginForm import UserLoginForm
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from common.jwt_util import generate_access_token, generate_refresh_token

def login_sms(request):
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
def access_token(request):
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
def login_wx(request):
    code = verify_util.is_token2(request.GET.get('code'))
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
    call = verify_util.is_call(request.GET.get('code'))
    if call:
        code = common.randint()
        data = ManeuGuest.objects.filter(phone=call).all().update(remark=code)
        if data:
            response = common.sendsms(call, code)
            if response['Code'] == 'OK':
                content = {'status': True, 'message': '请求成功', 'content': {}, 'token': ''}
            else:
                content = {'status': False, 'message': '短信发送失败，今日次数用完了', 'content': {}, 'token': ''}
        else:
            content = {'status': False, 'message': '请求失败', 'content': {}, 'token': ''}
    else:
        content = {'status': False, 'message': '登录失败：请提交正确的手机号', 'content': {}, 'token': ''}
    return JsonResponse(content)


def order_verify(request):
    index_id = verify_util.is_uuid(request.GET.get('index_id'))
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
    index_id = verify_util.is_uuid(request.GET.get('index_id'))
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
    index_id = verify_util.is_uuid(request.GET.get('index_id'))
    if index_id:

        try:
            data = ManeuReport.objects.filter(id=index_id).first()
            content = {'status': True, 'message': '请求成功', 'content': {'time': data.time, 'plan': data.plan, 'os_va': data.os_va, 'os_cyl': data.os_cyl, 'os_sph': data.os_sph, 'os_ax': data.os_ax, 'od_va': data.od_va, 'od_cyl': data.od_cyl, 'od_sph': data.od_sph, 'od_ax': data.od_ax}}
        except Exception as e:
            content = {'status': False, 'message': str(e), 'content': {}, 'token': ''}


    else:
        content = {'status': False, 'message': '请提交正确的参数', 'content': {}, 'token': ''}
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


def order_list(request):
    token = verify_util.is_uuid(request.GET.get('token'))
    if token:

        remark = str(uuid.uuid4())
        guest = ManeuGuest.objects.filter(remark=token).first()
        if ManeuGuest.objects.filter(remark=token).update(remark=remark) != 0:
            data = ManeuOrder.objects.filter(phone=guest.phone, status=3).order_by('-time').all().values('id', 'name', 'time', 'phone', 'remark')
            return JsonResponse({'status': True, 'message': '', 'content': list(data)})
    else:
        content = {'status': False, 'message': '请重新登录', 'content': {}, 'token': ''}


    return JsonResponse(content)


def report_list(request):
    token = verify_util.is_uuid(request.GET.get('token'))

    guest = ManeuGuest.objects.filter(remark=token).first()
    if guest:
        remark = str(uuid.uuid4())
        guest_update = ManeuGuest.objects.filter(remark=token).update(remark=remark)

        data = ManeuReport.objects.filter(phone=guest.phone, status=2).order_by('-time').all().values('id', 'name', 'time', 'phone', 'remark')
        return JsonResponse({'status': True, 'message': '', 'content': list(data)})

    else:
        content = {'status': False, 'message': '请重新登录。', 'content': {}, 'token': ''}

    return JsonResponse(content)


def store_list(request):
    token = verify_util.is_uuid(request.GET.get('token'))

    guest = ManeuGuest.objects.filter(remark=token).first()
    if guest:
        remark = str(uuid.uuid4())
        guest_update = ManeuGuest.objects.filter(remark=token).update(remark=remark)

        data = ManeuStore.objects.filter(phone=guest.phone).order_by('-time').all().values('id', 'name', 'time', 'phone', 'remark')
        return JsonResponse({'status': True, 'message': '', 'content': list(data)})

    else:
        content = {'status': False, 'message': '请重新登录。', 'content': {}, 'token': ''}

    return JsonResponse(content)


def repair_list(request):
    token = verify_util.is_uuid(request.GET.get('token'))

    guest = ManeuGuest.objects.filter(remark=token).first()
    if guest:
        remark = str(uuid.uuid4())
        guest_update = ManeuGuest.objects.filter(remark=token).update(remark=remark)

        data = ManeuRepair.objects.filter(phone=guest.phone).order_by('-time').all().values('id', 'name', 'time', 'phone', 'remark')
        return JsonResponse({'status': True, 'message': '', 'content': list(data)})

    else:
        content = {'status': False, 'message': '请重新登录。', 'content': {}, 'token': ''}

    return JsonResponse(content)


def order_detail(request):
    code = verify_util.is_uuid(request.GET.get('code'))

    if code:

        try:
            data = ManeuOrder.objects.filter(id=code).first()
            content = {'status': True, 'message': '请求成功', 'content': model_to_dict(data)}
        except Exception as e:
            content = {'status': False, 'message': str(e), 'content': {}}
    else:
        content = {'status': False, 'message': '请重新登录', 'content': {}, 'token': ''}

    return JsonResponse(content)


def store_detail(request):
    code = verify_util.is_uuid(request.GET.get('code'))

    if code:

        try:
            data = ManeuStore.objects.filter(id=code).first()
            content = {'status': True, 'message': '请求成功', 'content': model_to_dict(data)}
        except Exception as e:
            content = {'status': False, 'message': str(e), 'content': {}}
    else:
        content = {'status': False, 'message': '请重新登录', 'content': {}, 'token': ''}

    return JsonResponse(content)


def guest_detail(request):
    code = verify_util.is_uuid(request.GET.get('code'))

    if code:

        try:
            data = ManeuGuest.objects.filter(id=code).first()
            content = {'status': True, 'message': '请求成功', 'content': model_to_dict(data)}
        except Exception as e:
            content = {'status': False, 'message': str(e), 'content': {}}
    else:
        content = {'status': False, 'message': '请重新登录', 'content': {}, 'token': ''}

    return JsonResponse(content)


def report_detail(request):
    code = verify_util.is_uuid(request.GET.get('code'))

    if code:

        try:
            data = ManeuReport.objects.filter(id=code).first()
            content = {'status': True, 'message': '请求成功', 'content': model_to_dict(data)}
        except Exception as e:
            content = {'status': False, 'message': str(e), 'content': {}}
    else:
        content = {'status': False, 'message': '请重新登录', 'content': {}, 'token': ''}

    return JsonResponse(content)


def repair_detail(request):
    code = verify_util.is_uuid(request.GET.get('code'))

    if code:

        try:
            data = ManeuRepair.objects.filter(id=code).first()
            content = {'status': True, 'message': '请求成功', 'content': model_to_dict(data)}
        except Exception as e:
            content = {'status': False, 'message': str(e), 'content': {}}


    return JsonResponse(content)
