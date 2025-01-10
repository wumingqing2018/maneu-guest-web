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
    code = is_call(request.GET.get('code'))
    text = is_code(request.GET.get('text'))
    data = []

    if code:
        guest = list(ManeuGuest.objects.filter(phone=code).all().values_list('id', flat=True))

        if text == "100001":
            data.extend(
                ManeuOrder.objects.filter(guest_id__in=guest).order_by('-time').all().values('id', 'name', 'time', 'phone', 'remark'))
            return JsonResponse({'status': True, 'message': '', 'content': data})
        elif text == "100002":
            data = {'id': [], 'time': [], 'AL': [], 'VA': [], 'SPH': [], 'CYL': [], 'OD_VA': [], 'OS_VA': [],
                    'OD_SPH': [], 'OS_SPH': [], 'OD_CYL': [], 'OS_CYL': [], 'OD_AL': [], 'OS_AL': []}

            report = ManeuReport.objects.filter(guest_id__in=guest).order_by('-time').all()
            for i in report:
                try:
                    content = json.loads(i.content)
                    data['time'].append(i.time.strftime("%Y-%m-%d"))
                    data['id'].append(i.id)
                    data['AL'].append(24)
                    data['VA'].append(1.00)
                    data['CYL'].append(0)
                    data['SPH'].append(0)
                except:
                    continue

                try:
                    data['OD_AL'].append(format(float(content['OD']['AL']), '.2f'))
                except:
                    data['OD_AL'].append(0.00)
                try:
                    data['OD_VA'].append(format(float(content['OD']['AL']), '.2f'))
                except:
                    data['OD_VA'].append(0.00)
                try:
                    data['OD_SPH'].append(format(float(content['OD']['AL']), '.2f'))
                except:
                    data['OD_SPH'].append(0.00)
                try:
                    data['OD_CYL'].append(format(float(content['OD']['AL']), '.2f'))
                except:
                    data['OD_CYL'].append(0.00)

                try:
                    data['OS_AL'].append(format(float(content['OS']['AL']), '.2f'))
                except:
                    data['OS_AL'].append(0.00)
                try:
                    data['OS_VA'].append(format(float(content['OS']['AL']), '.2f'))
                except:
                    data['OS_VA'].append(0.00)
                try:
                    data['OS_SPH'].append(format(float(content['OS']['AL']), '.2f'))
                except:
                    data['OS_SPH'].append(0.00)
                try:
                    data['OS_CYL'].append(format(float(content['OS']['AL']), '.2f'))
                except:
                    data['OS_CYL'].append(0.00)
            return JsonResponse({'status': True, 'message': '', 'content': data})
        elif text == "100003":
            data.extend(ManeuService.objects.filter(guest_id__in=guest).order_by('-time').all().values('id', 'time'))
            return JsonResponse({'status': True, 'message': '', 'content': data})

    return JsonResponse({'status': False, 'message': '', 'content': {}})


def get_detail(request):
    code = is_uuid(request.GET.get('code'))
    text = is_code(request.GET.get('text'))

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
