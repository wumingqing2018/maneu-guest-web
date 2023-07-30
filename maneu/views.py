import requests
from django.shortcuts import render, HttpResponse


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
    print(access_token)
    url = 'https://api.weixin.qq.com/wxa/business/getuserphonenumber?access_token='+access_token['access_token']
    # data2 = {"code": request.GET.get('code')}
    data2 = {"code": '5a8c07a4d0e4fe4c10d8c55301f5f262db226322b33d3d5003b5345a7b2832f6'}

    phoneCall = requests.post(url, data2).json()
    print(phoneCall)
