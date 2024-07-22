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
        data = ManeuOrder.objects.filter(guess_id=request.GET.get('code')).order_by('-time').all().values('id', 'time')
        content = {'status': True, 'message': 'success', 'content': list(data)}
    return JsonResponse(content)


def getOrderDetail(request):
    if(request.GET.get('code') == ''):
        content = {'status': False, 'message': 'code is none', 'data': {}}
    else:
        order = ManeuOrderV2.objects.filter(id=request.GET.get('code')).first()
        store = ManeuStore.objects.filter(id=order.store_id).first()
        vision = ManeuVision.objects.filter(id=order.vision_id).first()
        content = {'status': True, 'message': 'success', 'time': order.time, 'store': json.loads(store.content), 'vision': json.loads(vision.content)}
    return JsonResponse(content)


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
    if(request.GET.get('code') == ''):
        content = {'status': False, 'message': 'code is none', 'data': {}}
    else:
        data = ManeuService.objects.filter(guess_id=request.GET.get('code')).order_by('-time').all().values('time', 'id')
        content = {'status': True, 'message': 'success', 'content': list(data)}
    return JsonResponse(content)


def getServiceDetail(request):
    if(request.GET.get('code') == ''):
        content = {'status': False, 'message': 'code is none', 'data': {}}
    else:
        data = ManeuService.objects.filter(guess_id=request.GET.get('code')).order_by('-time').first()
        content = {'status': True, 'message': 'success', 'content': list(data)}
    return JsonResponse(content)

def Test(request):
    content = list(ManeuOrder.objects.filter(phone='13640651582').order_by('-time').all().values('id', 'time'))
    return JsonResponse(content, safe=False)