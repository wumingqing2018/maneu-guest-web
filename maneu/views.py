import json, os, re,random
from encodings.utf_7 import encode
from http.client import responses

from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkcore.client import AcsClient
from aliyunsdkdysmsapi.request.v20170525.SendSmsRequest import SendSmsRequest
from django.http import JsonResponse
from django.shortcuts import render

from maneu.models import *


def index(request):
    return render(request, 'index.html')


def login(request):
    pattern_call = re.compile(r'^1[3-9]\d{9}$')
    pattern_code = re.compile(r'^\d{6}$')

    call = request.GET.get('call')
    code = request.GET.get('code')

    if pattern_call.match(call) is not None:
        if pattern_code.match(code) is not None:
            data = ManeuGuess.objects.filter(phone=call, remark=code).first()
            content = {'status': True, 'message': 'success',
                       'content': {'call': data.phone, 'name': data.name, 'id': data.id}}
        else:
            content = {'status': False, 'message': 'code is warning', 'data': {}}
    else:
        content = {'status': False, 'message': 'call is none', 'data': {}}

    return JsonResponse(content)


def get_list(request):
    pattern = re.compile(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    code = request.GET.get('code')

    if pattern.match(str(code)) is not None:
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
    if request.GET.get('text') == "Order":
        try:
            order = ManeuOrderV2.objects.filter(id=request.GET.get('code')).first()
            store = ManeuStore.objects.filter(id=order.store_id).first()
            vision = ManeuVision.objects.filter(id=order.vision_id).first()
            content = {'status': True,
                       'message': 'success',
                       'time': order.time,
                       'store': json.loads(store.content),
                       'vision': json.loads(vision.content)}
        except Exception as e:
            content = {'status': False, 'message': e}
    elif request.GET.get('text') == "Service":
        try:
            data = ManeuService.objects.filter(guess_id=request.GET.get('code')).order_by('-time').first().values(
                'time', 'content')
            content = {'status': True, 'message': 'success', 'content': list(data)}
        except Exception as e:
            content = {'status': False, 'message': e}
    elif request.GET.get('text') == "Refraction":
        try:
            data = json.loads(ManeuRefraction.objects.filter(id=request.GET.get('code')).first().content)
            content = {'status': True, 'message': 'success', 'content': data}
        except Exception as e:
            content = {'status': False, 'message': e}
    else:
        content = {'status': False, 'message': 'code is none'}
    return JsonResponse(content)


def sendsms(request):
    pattern = re.compile(r'^1[3-9]\d{9}$')
    phone_number = str(request.GET.get('code'))

    if pattern.match(phone_number) is not None:
        random_num = random.randint(111111,999999)
        data = ManeuGuess.objects.filter(phone=phone_number).update(remark=random_num)
        if data is not None:
            # Please ensure that the environment variables ALIBABA_CLOUD_ACCESS_KEY_ID and ALIBABA_CLOUD_ACCESS_KEY_SECRET are set.
            credentials = AccessKeyCredential(os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'],os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'])
            # use STS Token
            # credentials = StsTokenCredential(os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'], os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'], os.environ['ALIBABA_CLOUD_SECURITY_TOKEN'])
            client = AcsClient(region_id='cn-shenzhen', credential=credentials)

            request = SendSmsRequest()
            request.set_accept_format('json')
            request.set_SignName("徕可")
            request.set_TemplateCode("SMS_471990239")
            request.set_PhoneNumbers(phone_number)
            request.set_TemplateParam({'code': random_num})

            response = eval(client.do_action_with_exception(request))
            print(type(response))
            if response.code =='OK':
                content = {'status': True, 'message': response.code, 'data': {}}
            else:
                content = {'status': True, 'message': response.code, 'data': {}}

        else:
            content = {'status': False, 'message': 'phone is :none', 'data': {}}
    else:
        content = {'status': False, 'message': 'code is :none', 'data': {}}

    return JsonResponse(content)