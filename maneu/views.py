import json
import math

import requests
from django.http import JsonResponse
from django.shortcuts import render

from maneu.models import *


def index(request):
    return render(request, 'index.html')


def login(request):
    if(request.GET.get('call') == '' or request.GET.get('code') == ''):
        content = {'status': False, 'message': 'call or code is none', 'data': {}}
    else:
        data = ManeuGuess.objects.filter(phone=request.GET.get('call')).first()
        content = {'status': True, 'message': 'success', 'content': {'call': data.phone, 'name': data.name, 'id': data.id}}
    return JsonResponse(content)


def getPhoneCall(request):
    getAccessTokenUrl = 'https://api.weixin.qq.com/cgi-bin/token'
    data = {"appid": "wxf48b774de9be5613",
            "secret": "9b0d309b24e5cd3298f67f570ce5bfde",
            "grant_type": "client_credential"
            }
    access_token = requests.get(getAccessTokenUrl, data).json()

    getPhoneUrl = 'https://api.weixin.qq.com/wxa/business/getuserphonenumber?access_token='+access_token['access_token']
    data = {'code': request.GET.get('code')}
    phone = requests.post(getPhoneUrl, json.dumps(data)).json()
    return JsonResponse(phone)


def getOrderList(request):
    if(request.GET.get('code') == ''):
        content = {'status': False, 'message': 'code is none', 'data': {}}
    else:
        data = list(ManeuOrder.objects.filter(guess_id=request.GET.get('code')).order_by('-time').all().values('id', 'time'))
        content = {'status': True, 'message': 'success', 'content': data}
    return JsonResponse(content)


def getOrderDetail(request):
    content = []
    order = ManeuOrder.objects.filter(id=request.GET.get('code')).first()
    store_content = json.loads(ManeuStore.objects.filter(id=order.store_id).first().content)
    store_length = math.ceil(len(store_content)/5)
    store_list = []
    for i in range(1, store_length+1):
        store_list.append({'arg0': store_content['arg'+ str(i) +'0'],
                           'arg1': store_content['arg'+ str(i) +'1'],
                           'arg2': store_content['arg'+ str(i) +'2'],
                           'arg3': store_content['arg'+ str(i) +'3'],
                           'arg4': store_content['arg'+ str(i) +'4'],
                           })
    try:
        content.append(store_content['remark'])
    except:
        content.append('')
    content.append(store_list)
    content.append(json.loads(ManeuVision.objects.filter(id=order.vision_id).first().content))
    return JsonResponse(content, safe=False)


def getReportList(request):
    if(request.GET.get('code') == ''):
        content = {'status': False, 'message': 'code is none', 'data': {}}
    else:
        data = ManeuRefraction.objects.filter(guess_id=request.GET.get('code')).order_by('-time').all().values('id', 'time')
        content = {'status': True, 'message': 'success', 'content': list(data)}
    return JsonResponse(content)


def getReportDetail(request):
    content = json.loads(ManeuRefraction.objects.filter(id=request.GET.get('code')).first().content)
    return JsonResponse(content, safe=False)


def getServiceList(request):
    content = list(ManeuService.objects.filter().order_by('-time').all().values('time', 'id'))
    print(content)
    return JsonResponse(content,safe=False)


def getServiceDetail(request):
    content = json.loads(ManeuService.objects.filter(id=request.GET.get('code')).first())
    return JsonResponse(content, safe=False)


def Test(request):
    content = list(ManeuOrder.objects.filter(phone='13640651582').order_by('-time').all().values('id', 'time'))
    return JsonResponse(content, safe=False)