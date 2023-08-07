import json
import math

import requests
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse

from maneu.models import ManeuOrderV2
from maneu.models import ManeuStore
from maneu.models import ManeuSubjectiveRefraction
from maneu.models import ManeuVisionSolutions


def index(request):
    return render(request, 'maneu/index.html')


def login(request):
    url = 'https://api.weixin.qq.com/sns/jscode2session'
    data = {"appid": "wxf48b774de9be5613",
            "secret": "9a7ac5730b249c8ccc8a2b410631935b",
            "grant_type": "authorization_code",
            "js_code": request.GET.get('js_code')
            }
    reecho = requests.get(url, data)
    return HttpResponse(reecho, reecho.json())


def getPhoneCall(request):
    getAccessTokenUrl = 'https://api.weixin.qq.com/cgi-bin/token'
    data = {"appid": "wxf48b774de9be5613",
            "secret": "9a7ac5730b249c8ccc8a2b410631935b",
            "grant_type": "client_credential"
            }
    access_token = requests.get(getAccessTokenUrl, data).json()
    return HttpResponse(access_token['access_token'])


def getOrderList(request):
    content = list(ManeuOrderV2.objects.filter(phone=request.GET.get('code')).order_by('-time').all().values('id', 'time'))
    return JsonResponse(content, safe=False)


def getOrderDetail(request):
    content = []
    order = ManeuOrderV2.objects.filter(id=request.GET.get('code')).first()
    store_content = json.loads(ManeuStore.objects.filter(id=order.store_id).first().content)
    store_length = math.ceil(len(store_content)/5)
    store_list = []
    for i in range(1, store_length):
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
    content.append(json.loads(ManeuVisionSolutions.objects.filter(id=order.visionsolutions_id).first().content))
    return JsonResponse(content, safe=False)


def getReportList(request):
    content = list(ManeuSubjectiveRefraction.objects.filter(phone=request.GET.get('code')).order_by('-time').all().values('id', 'time'))
    return JsonResponse(content, safe=False)


def getReportDetail(request):
    content = list(ManeuSubjectiveRefraction.objects.filter(id=request.GET.get('code')).all())
    return JsonResponse(content, safe=False)
