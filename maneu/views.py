import requests
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from maneu.models import ManeuOrderV2
from maneu.models import ManeuSubjectiveRefraction
from django.core import serializers


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
    phone = ManeuOrderV2.objects.filter(id=request.GET.get('code')).all()
    content = serializers.serialize("json", phone)
    return JsonResponse(content, safe=False)


def getReportList(request):
    content = list(ManeuSubjectiveRefraction.objects.filter(phone=request.GET.get('code')).order_by('-time').all().values('id', 'time'))
    return JsonResponse(content, safe=False)


def getReportDetail(request):
    content = list(ManeuSubjectiveRefraction.objects.filter(id=request.GET.get('code')).order_by('-time').all().values('id', 'time'))
    return JsonResponse(content, safe=False)
