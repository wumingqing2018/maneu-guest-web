import json
import math

import requests
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse

from maneu.models import *


def index(request):
    return render(request, 'index.html')


def login(request):
    print('call:'+request.GET.get('call')+',code:'+request.GET.get('code'))
    if(request.GET.get('call') or request.GET.get('code') == ''):
        print('1')
    return HttpResponse('ok')



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
    print(phone)
    return JsonResponse(phone)

def getOrderList(request):
    # getAccessTokenUrl = 'https://api.weixin.qq.com/cgi-bin/token'
    # data = {"appid": "wxf48b774de9be5613",
    #         "secret": "9b0d309b24e5cd3298f67f570ce5bfde",
    #         "grant_type": "client_credential"
    #         }
    # access_token = requests.get(getAccessTokenUrl, data).json()
    #
    # getPhoneUrl = 'https://api.weixin.qq.com/wxa/business/getuserphonenumber?access_token='+access_token['access_token']
    # data = {'code': request.GET.get('code')}
    # phone = requests.post(getPhoneUrl, json.dumps(data)).json()
    #
    # if phone['errcode'] == 0:
    #     content = list(ManeuOrder.objects.filter(phone=phone['phone_info']['purePhoneNumber']).order_by('-time').all().values('id', 'time'))
    #     return JsonResponse(content, safe=False)
    # else:
    #     return JsonResponse(phone)
    guess = ManeuGuess.objects.filter(phone=request.GET.get('code')).order_by('-time').first()
    content = list(ManeuOrder.objects.filter(guess_id=guess.id).order_by('-time').all().values('id', 'time'))
    return JsonResponse(content, safe=False)


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
    # getAccessTokenUrl = 'https://api.weixin.qq.com/cgi-bin/token'
    # data = {"appid": "wxf48b774de9be5613",
    #         "secret": "9b0d309b24e5cd3298f67f570ce5bfde",
    #         "grant_type": "client_credential"
    #         }
    # access_token = requests.get(getAccessTokenUrl, data).json()
    #
    # getPhoneUrl = 'https://api.weixin.qq.com/wxa/business/getuserphonenumber?access_token='+access_token['access_token']
    # data = {'code': request.GET.get('code')}
    # phone = requests.post(getPhoneUrl, json.dumps(data)).json()
    # if phone['errcode'] == 0:
    #     guess = ManeuGuess.objects.filter(phone=phone['phone_info']['purePhoneNumber']).order_by('-time').first()
    #
    #     content = list(ManeuRefraction.objects.filter(guess_id=guess.id).order_by('-time').all().values('id', 'time'))
    #     return JsonResponse(content, safe=False)
    # else:
    #     return JsonResponse(phone)
    #
    guess = ManeuGuess.objects.filter(phone=request.GET.get('code')).order_by('-time').first()
    content = list(ManeuRefraction.objects.filter(guess_id=guess.id).order_by('-time').all().values('id', 'time'))
    return JsonResponse(content, safe=False)


def getReportDetail(request):
    content = json.loads(ManeuRefraction.objects.filter(id=request.GET.get('code')).first().content)
    return JsonResponse(content)


def Test(request):
    print(ManeuOrder.objects.filter(phone='111').order_by('-time').all().values('id', 'time'))
    content = list(ManeuOrder.objects.filter(phone='13640651582').order_by('-time').all().values('id', 'time'))
    return JsonResponse(content, safe=False)