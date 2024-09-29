from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkcore.client import AcsClient
from aliyunsdkdysmsapi.request.v20170525.SendSmsRequest import SendSmsRequest
from django.http import JsonResponse
from django.shortcuts import render

from maneu.models import *
from common.verify import *

import os, random, json

def index(request):
    return render(request, 'index.html')


def login(request):
    call = is_call(request.GET.get('call'))
    code = is_code(request.GET.get('code'))

    if call and code:
        data = ManeuGuess.objects.filter(phone=call, remark=code).all()
        if data:
            content = {'status': True, 'message': '100000', 'content': {'call': call, 'id': data.values('id')}}
        else:
            content = {'status': False, 'message': '100002', 'content': {}}
    else:
        content = {'status': False, 'message': '100001', 'content': {}}

    return JsonResponse(content)


def get_list(request):
    code = is_call(request.GET.get('code'))

    if code:
        if request.GET.get('text') == "Order":
            data = ManeuOrder.objects.filter(phone=code).order_by('-time').all().values('id', 'time')
            content = {'status': True, 'message': '100000', 'content': list(data)}
        elif request.GET.get('text') == "Service":
            data = ManeuService.objects.filter(phone=code).order_by('-time').all().values('id', 'time')
            content = {'status': True, 'message': '100000', 'content': list(data)}
        elif request.GET.get('text') == "Refraction":
            data = ManeuRefraction.objects.filter(phone=code).order_by('-time').all().values('id', 'time')
            content = {'status': True, 'message': '100000', 'content': list(data)}
        else:
            content = {'status': False, 'message': '100002', 'content': {}}
    else:
        content = {'status': False, 'message': '100001', 'content': {}}

    return JsonResponse(content)


def get_detail(request):
    code = is_uuid(request.GET.get('code'))

    if code:
        if request.GET.get('text') == "Order":
            order = ManeuOrderV2.objects.filter(id=code).first()
            store = ManeuStore.objects.filter(id=order.store_id).first()
            vision = ManeuVision.objects.filter(id=order.vision_id).first()
            content = {'status': True, 'message': '100000', 'content': {'time': order.time, 'remark':order.remark, 'store': json.loads(store.content), 'vision': json.loads(vision.content)}}
        elif request.GET.get('text') == "Service":
            data = ManeuService.objects.filter(guess_id=code).order_by('-time').first().values('time', 'content')
            content = {'status': True, 'message': '100000', 'content': data}
        elif request.GET.get('text') == "Refraction":
            data = json.loads(ManeuRefraction.objects.filter(id=code).first().content)
            content = {'status': True, 'message': '100000', 'content': data}
        else:
            content = {'status': False, 'message': '100002', 'content': {}}
    else:
        content = {'status': False, 'message': '100001', 'content': {}}

    return JsonResponse(content)


def sendsms(request):
    call = is_call(request.GET.get('code'))

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
                content = {'status': True, 'message': '100000', 'content': {}}
            else:
                content = {'status': False, 'message': '短息发送失败', 'content': {}}
        else:
            content = {'status': False, 'message': '100002', 'content': {}}
    else:
        content = {'status': False, 'message': '100001', 'content': {}}

    return JsonResponse(content)
