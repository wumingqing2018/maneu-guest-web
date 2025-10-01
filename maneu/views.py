import json

from django.http import JsonResponse
from django.shortcuts import render

from common import common
from common import verify
from maneu.models import *


def index(request):
    return render(request, 'index.html')


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
        print(phone)
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
    token = verify.is_uuid(request.GET.get('token'))
    text = verify.is_code(request.GET.get('text'))

    if token and text:
        guest = ManeuGuest.objects.filter(remark=token).first()
        if guest:
            remark = uuid.uuid4()
            guest1 = ManeuGuest.objects.filter(remark=token).update(remark=remark)
            if text == "100001":
                data = ManeuOrder.objects.filter(phone=guest.phone).order_by('-time').all().values('id', 'name', 'time',
                                                                                                   'phone', 'remark',
                                                                                                   'content')
                return JsonResponse({'status': True, 'message': '', 'content': list(data), 'token': remark})
            elif text == "100002":
                data = ManeuReport.objects.filter(phone=guest.phone).order_by('-time').all().values('id', 'name',
                                                                                                    'time', 'phone',
                                                                                                    'remark', 'content')
                return JsonResponse({'status': True, 'message': '', 'content': list(data), 'token': remark})
            elif text == "100003":
                data = ManeuService.objects.filter(phone=guest.phone).order_by('-time').all().values('id', 'time')
                return JsonResponse({'status': True, 'message': '', 'content': list(data), 'token': remark})
            else:
                return JsonResponse({'status': False, 'message': '错误参数', 'content': {}, 'token': remark})
        else:
            return JsonResponse({'status': False, 'message': '请重新登录', 'content': {}, 'token': ''})
    else:
        return JsonResponse({'status': False, 'message': '缺少参数', 'content': {}, 'token': ''})


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
                        order = ManeuOrder.objects.filter(id=code, guest_id=guest.id).first()
                        data = {'admin_id': order.admin_id,
                                'guest_id': order.guest_id,
                                'report_id': order.report_id,
                                'time': order.time.strftime("%Y-%m-%d %H:%M"),
                                'name': order.name,
                                'phone': order.phone,
                                'remark': order.remark,
                                'content': json.loads(order.content),
                                }
                        content = {'status': True, 'message': '100000', 'content': data, 'token': remark}
                    except Exception as e:
                        content = {'status': False, 'message': str(e), 'content': {}, 'token': remark}
                elif request.GET.get('text') == "100002":
                    try:
                        store = ManeuStore.objects.filter(id=code).first()
                        content = {'status': True, 'message': '100000', 'content': json.loads(store.content),
                                   'token': remark}
                    except Exception as e:
                        content = {'status': False, 'message': str(e), 'content': {}, 'token': remark}
                elif request.GET.get('text') == "100003":
                    try:
                        report = ManeuReport.objects.filter(id=code).first()
                        data = {'admin_id': report.admin_id,
                                'name': report.name,
                                'phone': report.phone,
                                'time': report.time.strftime("%Y-%m-%d %H:%M"),
                                'content': json.loads(report.content)
                                }
                        content = {'status': True, 'message': '100000', 'content': data, 'token': remark}
                    except Exception as e:
                        content = {'status': False, 'message': str(e), 'content': {}, 'token': remark}
                elif request.GET.get('text') == "100004":
                    try:
                        guest = ManeuGuest.objects.filter(id=code).first()
                        data = {
                            'time': guest.time,
                            'name': guest.name,
                            'phone': guest.phone,
                            'remark': guest.remark,
                            'sex': guest.sex,
                            'age': guest.age,
                            'dfh': guest.dfh,
                            'ot': guest.ot,
                            'em': guest.em,
                        }
                        content = {'status': True, 'message': '100000', 'content': data, 'token': remark}
                    except Exception as e:
                        content = {'status': False, 'message': str(e), 'content': {}, 'token': remark}
                elif request.GET.get('text') == "100005":
                    try:
                        admin = ManeuAdmin.objects.filter(id=code).first()
                        data = {'location': admin.location,
                                'nickname': admin.nickname,
                                'content': admin.content,
                                'phone': admin.phone
                                }
                        content = {'status': True, 'message': '100000', 'content': data, 'token': remark}
                    except Exception as e:
                        content = {'status': False, 'message': str(e), 'content': {}, 'token': remark}
                elif request.GET.get('text') == "100006":
                    try:
                        service = ManeuService.objects.filter(guest_id=code).first()
                        data = {
                            'time': service.time,
                            'name': service.name,
                            'phone': service.phone,
                            'remark': service.remark,
                        }
                        content = {'status': True, 'message': '100000', 'content': data, 'token': remark}
                    except Exception as e:
                        content = {'status': False, 'message': str(e), 'content': {}, 'token': remark}
                elif request.GET.get('text') == "100007":
                    try:
                        ManeuVerify.objects.create(order_id=code, guest_id=guest.id, name=guest.name, phone=guest.phone,
                                                   time=common.current_time())
                        data = ManeuVerify.objects.filter(order_id=code).order_by('-time').all().values('time')
                        content = {'status': True, 'message': '100000', 'content': list(data), 'token': remark}
                    except Exception as e:
                        content = {'status': False, 'message': str(e), 'content': {}, 'token': remark}
                else:
                    content = {'status': False, 'message': '100001', 'content': {}, 'token': remark}
            else:
                content = {'status': False, 'message': '100002', 'content': {}, 'token': ''}
        else:
            content = {'status': False, 'message': 'code is wrong'+request.GET.get('code'), 'content': {}, 'token': ''}
    else:
        content = {'status': False, 'message': '100004', 'content': {}, 'token': ''}

    return JsonResponse(content)


def get_verify(request):
    order_id = verify.is_uuid(request.GET.get('order_id'))
    token = verify.is_uuid(request.GET.get('token'))
    if order_id and token == request.session.get('token'):
        token = uuid.uuid4()
        request.session['token'] = token
        Order = ManeuOrder.objects.filter(id=order_id).first()
        if Order:
            if ManeuVerify.objects.create(order_id=Order.id, time=common.current_time()):
                data = ManeuVerify.objects.filter(order_id=Order.id).all().values('time')
                content = {'status': True, 'message': '', 'content': {'data': list(data), 'token': token}}
            else:
                content = {'status': False, 'message': '查询失败', 'content': {'data': [], 'token': token}}
        else:
            content = {'status': False, 'message': '不存在订单', 'content': {'data': [], 'token': token}}
    else:
        content = {'status': False, 'message': '非法格式', 'content': {}, 'token': ''}
    return JsonResponse(content)
