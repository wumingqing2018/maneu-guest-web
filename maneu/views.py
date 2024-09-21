import json
import os
import random

from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkcore.client import AcsClient
from aliyunsdkdysmsapi.request.v20170525.SendSmsRequest import SendSmsRequest
from django.http import JsonResponse
from django.shortcuts import render

from maneu.models import *
from common import verify

def index(request):
    return render(request, 'index.html')


def login(request):
    call = verify.is_call(request.GET.get('call'))
    code = verify.is_code(request.GET.get('code'))

    if call and code:
        data = ManeuGuess.objects.filter(phone=call, remark=code).first()
        if data:
            content = {'status': True, 'message': 'success', 'content': {'call': data.phone, 'name': data.name, 'id': data.id} }
        else:
            content = {'status': False, 'message': 'call is none', 'data': {}}
    else:
        content = {'status': False, 'message': 'call or code is warning', 'data': {}}

    return JsonResponse(content)


def get_list(request):
    code = verify.is_uuid(request.GET.get('code'))

    if code:
        if request.GET.get('text') == "Order":
            data = ManeuOrder.objects.filter(guess_id=code).order_by('-time').all().values('id', 'time')
            content = {'status': True, 'message': 'success', 'content': list(data)}
        elif request.GET.get('text') == "Service":
            data = ManeuService.objects.filter(guess_id=code).order_by('-time').all().values('id', 'time')
            content = {'status': True, 'message': 'success', 'content': list(data)}
        elif request.GET.get('text') == "Refraction":
            data = ManeuRefraction.objects.filter(guess_id=code).order_by('-time').all().values('id', 'time')
            content = {'status': True, 'message': 'success', 'content': list(data)}
        else:
            content = {'status': False, 'message': 'code is none', 'data': {}}
    else:
        content = {'status': False, 'message': 'code is none', 'data': {}}

    return JsonResponse(content)


def get_detail(request):
    code = verify.is_uuid(request.GET.get('code'))

    if code:
        if request.GET.get('text') == "Order":
            order = ManeuOrderV2.objects.filter(id=request.GET.get('code')).first()
            store = ManeuStore.objects.filter(id=order.store_id).first()
            vision = ManeuVision.objects.filter(id=order.vision_id).first()
            content = {'status': True,
                       'message': 'success',
                       'time': order.time,
                       'store': json.loads(store.content),
                       'vision': json.loads(vision.content)}
        elif request.GET.get('text') == "Service":
            data = ManeuService.objects.filter(guess_id=request.GET.get('code')).order_by('-time').first().values('time', 'content')
            content = {'status': True, 'message': 'success', 'content': list(data)}
        elif request.GET.get('text') == "Refraction":
            data = json.loads(ManeuRefraction.objects.filter(id=request.GET.get('code')).first().content)
            content = {'status': True, 'message': 'success', 'content': data}
        else:
            content = {'status': False, 'message': 'code is none'}
    else:
        content = {'status': False, 'message': 'code is none', 'data': {}}

    return JsonResponse(content)


def sendsms(request):
    call = verify.is_call(request.GET.get('call'))

    if call:
        random_num = random.randint(111111, 999999)
        data = ManeuGuess.objects.filter(phone=call).update(remark=random_num)
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
                content = {'status': True, 'message': 'OK', 'data': {}}
            else:
                content = {'status': False, 'message': '', 'data': response}
        else:
            content = {'status': False, 'message': 'phone is :none', 'data': {}}
    else:
        content = {'status': False, 'message': 'code is :none', 'data': {}}

    return JsonResponse(content)
