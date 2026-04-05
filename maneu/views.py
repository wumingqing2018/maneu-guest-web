import json

from django.http import JsonResponse
from django.shortcuts import render

from common import common
from common import verify
from maneu.models import *
from django.forms.models import model_to_dict
import uuid


def index(request):
    if verify.is_mobile(request.META.get("HTTP_USER_AGENT")):
        return render(request, 'index_P.html')
    else:
        return render(request, 'index_C.html')


def verify_order(request):
    order_id = verify.is_uuid(request.GET.get('order_id'))
    if order_id:


        try:
            data = ManeuOrder.objects.filter(id=order_id).first()
            data_time = data.time
            data_data = json.loads(data.content)
            content = {'status': True, 'message': '100000', 'content': {'time': data_time, 'data': data_data}}
        except Exception as e:
            content = {'status': False, 'message': str(e), 'content': {}, 'token': ''}


    else:
        content = {'status': False, 'message': '非法格式', 'content': {}, 'token': ''}
    return render(request, 'verify_order.html', content)



def verify_store(request):
    store_id = verify.is_uuid(request.GET.get('store_id'))
    if store_id:


        try:
            data = ManeuStore.objects.filter(id=store_id).first()
            data_time = data.time
            data_data = json.loads(data.content)
            content = {'status': True, 'message': '100000', 'content': {'time': data_time, 'data': data_data}}
        except Exception as e:
            content = {'status': False, 'message': str(e), 'content': {}, 'token': ''}


    else:
        content = {'status': False, 'message': '非法格式', 'content': {}, 'token': ''}
    return render(request, 'verify_store.html', content)


def login(request):
    call = verify.is_call(request.GET.get('call'))
    code = verify.is_code(request.GET.get('code'))

    if call and code:
        token = uuid.uuid4()
        guest = ManeuGuest.objects.filter(phone=call).all().update(remark=token)
        if guest:
            content = {'status': True, 'message': '100000', 'content': {}, 'token': token}
        else:
            content = {'status': False, 'message': '100002', 'content': {}, 'token': ''}
    else:
        content = {'status': False, 'message': '100001', 'content': {}, 'token': ''}

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
                content = {'status': True, 'message': '100000', 'content': {}, 'token': token}
            else:
                content = {'status': False, 'message': '100003', 'content': {}, 'token': ''}
        else:
            data_token = common.get_miniprogram_token()['access_token']
            ManeuAdmin.objects.all().update(content=data_token)
            phone = common.get_phone_number(code, data_token)
            if phone['status']:
                token = uuid.uuid4()
                guest = ManeuGuest.objects.filter(phone=phone['message']).update(remark=token)
                if guest != 0:
                    content = {'status': True, 'message': '100000', 'content': {}, 'token': token}
                else:
                    content = {'status': False, 'message': '100003', 'content': {}, 'token': ''}
            else:
                content = {'status': False, 'message': '100002', 'content': {}, 'token': ''}
    else:
        content = {'status': False, 'message': '100001', 'content': {}, 'token': ''}

    return JsonResponse(content)


def sendsms(request):
    call = verify.is_call(request.GET.get('code'))
    if call:
        code = common.randint()
        data = ManeuGuest.objects.filter(phone=call).all().update(remark=code)
        if data:
            response = common.sendsms(call, code)
            if response['Code'] == 'OK':
                content = {'status': True, 'message': '100000', 'content': {}, 'token': ''}
            else:
                content = {'status': False, 'message': '短信发送失败，今日次数用完了', 'content': {}, 'token': ''}
        else:
            content = {'status': False, 'message': '100002', 'content': {}, 'token': ''}
    else:
        content = {'status': False, 'message': '100001', 'content': {}, 'token': ''}
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
    return JsonResponse({'status': True, 'message': '', 'content': data})


def get_list(request):
    text = verify.is_code(request.GET.get('text'))
    token = verify.is_uuid(request.GET.get('token'))

    guest = ManeuGuest.objects.filter(remark=token).first()
    if guest:
        remark = str(uuid.uuid4())
        guest_update = ManeuGuest.objects.filter(remark=token).update(remark=remark)

        if text == "100001":
            data = ManeuOrder.objects.filter(phone=guest.phone, status=3).order_by('-time').all().values('id', 'name', 'time', 'phone', 'remark')
            return JsonResponse({'status': True, 'message': '', 'content': list(data), 'token': remark})
        elif text == "100002":
            data = ManeuReport.objects.filter(phone=guest.phone, status=2).order_by('-time').all().values('id', 'name', 'time', 'phone', 'remark')
            return JsonResponse({'status': True, 'message': '', 'content': list(data), 'token': remark})
        elif text == "100003":
            data = ManeuRepair.objects.filter(phone=guest.phone).order_by('-time').all().values('id', 'name', 'time', 'phone', 'remark')
            return JsonResponse({'status': True, 'message': '', 'content': list(data), 'token': remark})
        else:
            content = {'status': False, 'message': 'text is wrong' + request.GET.get('text'), 'content': {}, 'token': ''}
    else:
        content = {'status': False, 'message': 'mark is wrong' + request.GET.get('token'), 'content': {}, 'token': ''}

    return JsonResponse(content)


def get_detail(request):
    code = verify.is_uuid(request.GET.get('code'))
    text = verify.is_code(request.GET.get('text'))
    token = verify.is_uuid(request.GET.get('token'))

    if text:
        if code:
            guest = ManeuGuest.objects.filter(remark=token).first()
            if guest:
                remark = uuid.uuid4()
                guest1 = ManeuGuest.objects.filter(remark=token).update(remark=remark)
                if request.GET.get('text') == "100001":
                    try:
                        data = ManeuOrder.objects.filter(id=code).first()
                        content = {'status': True, 'message': '100000', 'content': model_to_dict(data), 'token': remark}
                    except Exception as e:
                        content = {'status': False, 'message': str(e), 'content': {}, 'token': remark}
                elif request.GET.get('text') == "100002":
                    try:
                        store = ManeuStore.objects.filter(id=code).first()
                        content = {'status': True, 'message': '100000', 'content': json.loads(store.content), 'token': remark}
                    except Exception as e:
                        content = {'status': False, 'message': str(e), 'content': {}, 'token': remark}
                elif request.GET.get('text') == "100003":
                    try:
                        data = ManeuReport.objects.filter(id=code).first()
                        content = {'status': True, 'message': '100000', 'content': model_to_dict(data), 'token': remark}
                    except Exception as e:
                        content = {'status': False, 'message': str(e), 'content': {}, 'token': remark}
                elif request.GET.get('text') == "100004":
                    try:
                        data = ManeuGuest.objects.filter(id=code).first()
                        content = {'status': True, 'message': '100000', 'content': model_to_dict(data), 'token': remark}
                    except Exception as e:
                        content = {'status': False, 'message': str(e), 'content': {}, 'token': remark}
                elif request.GET.get('text') == "100005":
                    try:
                        data = ManeuAdmin.objects.filter(id=code).first()
                        content = {'status': True, 'message': '100000', 'content': model_to_dict(data), 'token': remark}
                    except Exception as e:
                        content = {'status': False, 'message': str(e), 'content': {}, 'token': remark}
                elif request.GET.get('text') == "100006":
                    try:
                        data = ManeuRepair.objects.filter(guest_id=code).first()
                        content = {'status': True, 'message': '100000', 'content': model_to_dict(data), 'token': remark}
                    except Exception as e:
                        content = {'status': False, 'message': str(e), 'content': {}, 'token': remark}
                elif request.GET.get('text') == "100007":
                    try:
                        ManeuVerify.objects.create(order_id=code, guest_id=guest.id, name=guest.name, call=guest.phone, time=common.current_time())
                        data = ManeuVerify.objects.filter(order_id=code).order_by('-time').all().values('time')
                        content = {'status': True, 'message': '100000', 'content': list(data), 'token': remark}
                    except Exception as e:
                        content = {'status': False, 'message': str(e), 'content': {}, 'token': remark}
                else:
                    content = {'status': False, 'message': 'text is wrong' + str(request.GET.get('text')), 'content': {}, 'token': ''}
            else:
                content = {'status': False, 'message': 'mark is wrong' + str(request.GET.get('token')), 'content': {}, 'token': ''}
        else:
            content = {'status': False, 'message': 'code is wrong' + str(request.GET.get('code')), 'content': {}, 'token': ''}
    else:
        content = {'status': False, 'message': 'text is wrong' + str(request.GET.get('text')), 'content': {}, 'token': ''}

    return JsonResponse(content)