import json
import os
import random

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

def test(request):
    return render(request, 'test.html')


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
    text = is_call(request.GET.get('text'))
    data = []

    if code:
        guest = list(ManeuGuest.objects.filter(phone=code).all().values_list('id', flat=True))

        if text == "100001":
            data.extend(ManeuOrder.objects.filter(guest_id__in=guest).order_by('-time').all().values('id', 'time'))
            return JsonResponse({'status': True, 'message': '', 'content': data})
        elif text == "100002":
            id = []
            time = []
            OD_VA = []
            OS_VA = []
            OD_SPH = []
            OS_SPH = []
            OD_CYL = []
            OS_CYL = []
            OD_AL = []
            OS_AL = []
            report = ManeuReport.objects.filter(guest_id__in=guest).order_by('-time').all()
            for i in report:
                content = json.loads(i.content)
                id.append(i.id)
                time.append(i.time.strftime("%Y-%m-%d"))
                if content['OD']['AL']:
                    OD_AL.append(float(content['OD']['AL']))
                else:
                    OD_AL.append(0.0)
                if content['OD']['VA']:
                    OD_VA.append(float(content['OD']['VA']))
                else:
                    OD_VA.append(0.0)
                if content['OD']['SPH']:
                    OD_SPH.append(float(content['OD']['SPH']))
                else:
                    OD_SPH.append(0.0)
                if content['OD']['CYL']:
                    OD_CYL.append(float(content['OD']['CYL']))
                else:
                    OD_CYL.append(0.0)

                if content['OS']['AL']:
                    OS_AL.append(float(content['OS']['AL']))
                else:
                    OS_AL.append(0.0)
                if content['OS']['VA']:
                    OS_VA.append(float(content['OS']['VA']))
                else:
                    OS_VA.append(0.0)
                if content['OS']['SPH']:
                    OS_SPH.append(float(content['OS']['SPH']))
                else:
                    OS_SPH.append(0.0)
                if content['OS']['CYL']:
                    OS_CYL.append(float(content['OS']['CYL']))
                else:
                    OS_CYL.append(0.0)
            return JsonResponse({'status': True, 'message': '', 'content': {'id': id, 'time': time, 'OD_VA': OD_VA, 'OS_VA': OS_VA, 'OD_SPH': OD_SPH,'OS_SPH': OS_SPH, 'OD_CYL': OD_CYL, 'OS_CYL': OS_CYL, 'OD_AL': OD_AL,'OS_AL': OS_AL}})
        elif text == "100003":
            data.extend(ManeuService.objects.filter(guest_id__in=guest).order_by('-time').all().values('id', 'time'))
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
    OD = []
    OS = []
    time = []
    if code:
        guest = ManeuGuest.objects.filter(phone=code).all()
        for i in guest:
            report_list = ManeuReport.objects.filter(guest_id=i.id).order_by('-time').all()
            for report in report_list:
                time.append(str(report.time))
                content = json.loads(report.content)
                if content['OD']['SPH']:
                    OD.append(int(content['OD']['SPH']))
                else:
                    OD.append(0)
                if content['OS']['SPH']:
                    OS.append(int(content['OS']['SPH']))
                else:
                    OS.append(0)

        return JsonResponse({'status': True, 'message': '', 'content': {'OD': OD, 'OS': OS, 'time': time}})

    return JsonResponse({'status': False, 'message': '', 'content': {}})
