import json
import os
import random
from os import lseek

from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkcore.client import AcsClient
from aliyunsdkdysmsapi.request.v20170525.SendSmsRequest import SendSmsRequest
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render

from common.verify import *
from maneu.models import *


def index(request):
    return render(request, 'index.html')


def login(request):
    call = is_call(request.GET.get('call'))
    code = is_code(request.GET.get('code'))

    if call and code:
        data = ManeuGuest.objects.filter(phone=call, remark=code).first()
        if data:
            content = {'status': True, 'message': '100000',
                       'content': {'call': data.phone, 'name': data.name, 'id': data.phone}}
        else:
            content = {'status': False, 'message': '100002', 'content': {}}
    else:
        content = {'status': False, 'message': '100001', 'content': {}}

    return JsonResponse(content)


def sendsms(request):
    call = is_call(request.GET.get('code'))

    if call:
        random_num = random.randint(100000, 999999)
        data = ManeuGuest.objects.filter(phone=call).update(remark=random_num)
        if data:
            # Please ensure that the environment variables ALIBABA_CLOUD_ACCESS_KEY_ID and ALIBABA_CLOUD_ACCESS_KEY_SECRET are set.
            credentials = AccessKeyCredential(os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'],
                                              os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'])
            # use STS Token
            # credentials = StsTokenCredential(os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'], os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'], os.environ['ALIBABA_CLOUD_SECURITY_TOKEN'])
            client = AcsClient(region_id='cn-shenzhen', credential=credentials)

            request = SendSmsRequest()
            request.set_accept_format('json')
            request.set_SignName("徕可")
            request.set_TemplateCode("SMS_471990239")
            request.set_PhoneNumbers(call)
            request.set_TemplateParam({'code': random_num})

            response = client.do_action_with_exception(request)
            response = eval(response)

            if response['Code'] == 'OK':
                content = {'status': True, 'message': '100000', 'content': {}}
            else:
                content = {'status': False, 'message': '短息发送失败', 'content': {}}
        else:
            content = {'status': False, 'message': '100002', 'content': {}}
    else:
        content = {'status': False, 'message': '100001', 'content': {}}

    return JsonResponse(content)


def get_index(request):
    data = [{
        "index": 'https://maneu.online/static/img/3.gif',
        "data": 'https://maneu.online/static/img/3.gif',
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
    code = is_call(request.GET.get('code'))
    data = []

    if code:
        guest = ManeuGuest.objects.filter(phone=code).all()

        if request.GET.get('text') == "Order":
            for i in guest:
                data.extend(ManeuOrder.objects.filter(guest_id=i.id).order_by('-time').all().values('id', 'time'))
            return JsonResponse({'status': True, 'message': '', 'content': data})
        elif request.GET.get('text') == "Report":
            for i in guest:
                data.extend(ManeuReport.objects.filter(guest_id=i.id).order_by('-time').all().values('id', 'time'))
            return JsonResponse({'status': True, 'message': '', 'content': data})
        elif request.GET.get('text') == "Service":
            for i in guest:
                data.extend(ManeuService.objects.filter(guest_id=i.id).order_by('-time').all().values('id', 'time'))
            return JsonResponse({'status': True, 'message': '', 'content': data})

    return JsonResponse({'status': False, 'message': '', 'content': {}})


def get_detail(request):
    code = is_uuid(request.GET.get('code'))

    if code:
        if request.GET.get('text') == "Order":
            order = ManeuOrder.objects.filter(id=code).first()
            content = {'status': True, 'message': '100000', 'content': model_to_dict(order)}
        elif request.GET.get('text') == "Store":
            store = ManeuStore.objects.filter(id=code).first()
            content = {'status': True, 'message': '100000', 'content': json.loads(store.content)}
        elif request.GET.get('text') == "Report":
            store = ManeuReport.objects.filter(id=code).first()
            content = {'status': True, 'message': '100000', 'content': json.loads(store.content)}
        elif request.GET.get('text') == "Service":
            data = ManeuService.objects.filter(guest_id=code).order_by('-time').first().values('time', 'content')
            content = {'status': True, 'message': '100000', 'content': data}
        else:
            content = {'status': False, 'message': '100002', 'content': {}}
    else:
        content = {'status': False, 'message': '100001', 'content': {}}

    return JsonResponse(content)


def get_visual(request):
    code = is_call(request.GET.get('code'))
    data = []

    if code:
        guest_list = ManeuGuest.objects.filter(phone=code).all().values('id')
        for guest in guest_list:
            print(guest)
            data.extend(ManeuReport.objects.filter(guest_id=guest.id).order_by('-time').all().values('time'))

        return JsonResponse({'status': True, 'message': '', 'content': data})

    return JsonResponse({'status': False, 'message': '', 'content': {}})
