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
        guest = ManeuGuest.objects.filter(phone=call, remark=code).first()
        if guest:
            token = common.generate_random_32hex()
            request.session['token'] = token
            request.session['guest_id'] = guest.id
            content = {'status': True, 'message': '100000', 'content': {'call': guest.phone, 'name': guest.name, 'token': token}}
        else:
            content = {'status': False, 'message': '100002', 'content': {}}
    else:
        content = {'status': False, 'message': '100001', 'content': {}}

    return JsonResponse(content)


def sendsms(request):
    call = verify.is_call(request.GET.get('code'))

    if call:
        code = common.randint()
        data = ManeuGuest.objects.filter(phone=call).update(remark=code)

        if data:
            response = common.sendsms(call, code)
            if response['Code'] == 'OK':
                content = {'status': True, 'message': '100000', 'content': {}}
            else:
                content = {'status': False, 'message': '短信发送失败，今日次数用完了', 'content': {}}
        else:
            content = {'status': False, 'message': '100002', 'content': {}}
    else:
        content = {'status': False, 'message': '100001', 'content': {}}

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
    code = verify.is_call(request.GET.get('code'))
    text = verify.is_code(request.GET.get('text'))

    if code:
        guest = list(ManeuGuest.objects.filter(phone=code).all().values_list('id', flat=True))

        if text == "100001":
            data = ManeuOrder.objects.filter(guest_id__in=guest).order_by('-time').all().values('id', 'name', 'time', 'phone', 'remark', 'content')
            return JsonResponse({'status': True, 'message': '', 'content': list(data)})
        elif text == "100002":
            data = ManeuReport.objects.filter(guest_id__in=guest).order_by('-time').all().values('id', 'name', 'time', 'phone', 'remark', 'content')
            return JsonResponse({'status': True, 'message': '', 'content': list(data)})
        elif text == "100003":
            data = ManeuService.objects.filter(guest_id__in=guest).order_by('-time').all().values('id', 'time')
            return JsonResponse({'status': True, 'message': '', 'content': data})
        else:
            return JsonResponse({'status': False, 'message': '', 'content': {}})
    else:
        return JsonResponse({'status': False, 'message': '', 'content': {}})


def get_detail(request):
    code = verify.is_uuid(request.GET.get('code'))
    text = verify.is_code(request.GET.get('text'))

    if code and text:
        if request.GET.get('text') == "100001":
            try:
                order = ManeuOrder.objects.filter(id=code).first()
                data = {'admin_id': order.admin_id,
                        'guest_id': order.guest_id,
                        'report_id': order.report_id,
                        'time': order.time.strftime("%Y-%m-%d %H:%M"),
                        'name': order.name,
                        'phone': order.phone,
                        'remark': order.remark,
                        'content': json.loads(order.content),
                        }
                content = {'status': True, 'message': '100000', 'content': data}
            except Exception as e:
                content = {'status': False, 'message': str(e), 'content': {}}
        elif request.GET.get('text') == "100002":
            try:
                store = ManeuStore.objects.filter(id=code).first()
                content = {'status': True, 'message': '100000', 'content': json.loads(store.content)}
            except Exception as e:
                content = {'status': False, 'message': str(e), 'content': {}}
        elif request.GET.get('text') == "100003":
            try:
                report = ManeuReport.objects.filter(id=code).first()
                data = {'admin_id': report.admin_id,
                        'name': report.name,
                        'phone': report.phone,
                        'time': report.time.strftime("%Y-%m-%d %H:%M"),
                        'content': json.loads(report.content)
                        }
                content = {'status': True, 'message': '100000', 'content': data}
            except Exception as e:
                content = {'status': False, 'message': str(e), 'content': {}}
        elif request.GET.get('text') == "100004":
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
            content = {'status': True, 'message': '100000', 'content': data}
        elif request.GET.get('text') == "100005":
            admin = ManeuAdmin.objects.filter(id=code).first()
            data = {'location': admin.location,
                    'nickname': admin.nickname,
                    'content': admin.content,
                    'phone': admin.phone
                    }
            content = {'status': True, 'message': '100000', 'content': data}
        elif request.GET.get('text') == "100006":
            try:
                service = ManeuService.objects.filter(guest_id=code).first()
                data = {
                    'time': service.time,
                    'name': service.name,
                    'phone': service.phone,
                    'remark': service.remark,
                }
                content = {'status': True, 'message': '100000', 'content': data}
            except Exception as e:
                content = {'status': False, 'message': str(e), 'content': {}}
        else:
            content = {'status': False, 'message': '100002', 'content': {}}
    else:
        content = {'status': False, 'message': '100001', 'content': {}}

    return JsonResponse(content)


def get_verify(request):
    order_id = verify.is_uuid(request.GET.get('order_id'))
    token = verify.is_token(request.GET.get('token'))
    if order_id and token:
        if token == request.session['token']:
            token = common.generate_random_32hex()
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
            content = {'status': False, 'message': '非法格式', 'content': {}}
    else:
        content = {'status': False, 'message': '非法格式', 'content': {}}
    return JsonResponse(content)

