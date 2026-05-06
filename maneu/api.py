import json

from django.http import JsonResponse

from common import common
from common import verify
from maneu.models import *
from django.forms.models import model_to_dict
import uuid


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


def login(request):
    call = verify.is_call(request.GET.get('call'))
    code = verify.is_code(request.GET.get('code'))

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
    code = verify.is_token2(request.GET.get('code'))
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
    token = verify.is_uuid(request.GET.get('token'))
    if token:

        remark = str(uuid.uuid4())
        guest = ManeuGuest.objects.filter(remark=token).first()
        if ManeuGuest.objects.filter(remark=token).update(remark=remark) != 0:
            data = ManeuOrder.objects.filter(phone=guest.phone, status=3).order_by('-time').all().values('id', 'name', 'time', 'phone', 'remark')
            return JsonResponse({'status': True, 'message': '', 'content': list(data), 'token': remark})
        else:
            content = {'status': False, 'message': '请重新登录', 'content': {}, 'token': ''}

    else:
        content = {'status': False, 'message': '请重新登录', 'content': {}, 'token': ''}

    return JsonResponse(content)


def report_list(request):
    token = verify.is_uuid(request.GET.get('token'))

    guest = ManeuGuest.objects.filter(remark=token).first()
    if guest:
        remark = str(uuid.uuid4())
        guest_update = ManeuGuest.objects.filter(remark=token).update(remark=remark)

        data = ManeuReport.objects.filter(phone=guest.phone, status=2).order_by('-time').all().values('id', 'name', 'time', 'phone', 'remark')
        return JsonResponse({'status': True, 'message': '', 'content': list(data), 'token': remark})

    else:
        content = {'status': False, 'message': '请重新登录。', 'content': {}, 'token': ''}

    return JsonResponse(content)


def store_list(request):
    token = verify.is_uuid(request.GET.get('token'))

    guest = ManeuGuest.objects.filter(remark=token).first()
    if guest:
        remark = str(uuid.uuid4())
        guest_update = ManeuGuest.objects.filter(remark=token).update(remark=remark)

        data = ManeuStore.objects.filter(phone=guest.phone).order_by('-time').all().values('id', 'name', 'time', 'phone', 'remark')
        return JsonResponse({'status': True, 'message': '', 'content': list(data), 'token': remark})

    else:
        content = {'status': False, 'message': '请重新登录。', 'content': {}, 'token': ''}

    return JsonResponse(content)


def repair_list(request):
    token = verify.is_uuid(request.GET.get('token'))

    guest = ManeuGuest.objects.filter(remark=token).first()
    if guest:
        remark = str(uuid.uuid4())
        guest_update = ManeuGuest.objects.filter(remark=token).update(remark=remark)

        data = ManeuRepair.objects.filter(phone=guest.phone).order_by('-time').all().values('id', 'name', 'time', 'phone', 'remark')
        return JsonResponse({'status': True, 'message': '', 'content': list(data), 'token': remark})

    else:
        content = {'status': False, 'message': '请重新登录。', 'content': {}, 'token': ''}

    return JsonResponse(content)


def order_detail(request):
    code = verify.is_uuid(request.GET.get('code'))
    mark = verify.is_uuid(request.GET.get('token'))

    if code or mark:
        remark = uuid.uuid4()
        guest = ManeuGuest.objects.filter(remark=mark).update(remark=remark)
        if guest != 0:
            try:
                data = ManeuOrder.objects.filter(id=code).first()
                content = {'status': True, 'message': '请求成功', 'content': model_to_dict(data), 'token': remark}
            except Exception as e:
                content = {'status': False, 'message': str(e), 'content': {}, 'token': remark}
        else:
            content = {'status': False, 'message': '请重新登录', 'content': {}, 'token': ''}
    else:
        content = {'status': False, 'message': '请重新登录', 'content': {}, 'token': ''}

    return JsonResponse(content)


def store_detail(request):
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