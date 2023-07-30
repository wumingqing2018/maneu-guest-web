import requests
from django.shortcuts import render, HttpResponse


def index(request):
    return render(request, 'maneu/index.html')


def login(request):
    code = request.GET.get('code')
    url = 'https://api.weixin.qq.com/cgi-bin/token'
    data = {"appid": "wxf48b774de9be5613",
            "secret": "9a7ac5730b249c8ccc8a2b410631935b",
            "grant_type": "client_credential"
            }
    reecho = requests.get(url, data)
    access_token = reecho.json()['access_token']
    url = 'https://api.weixin.qq.com/wxa/business/getuserphonenumber?access_token='+access_token
    data = {"code": code}
    reecho = requests.post(url=url, data=data)

    return HttpResponse(code, url, reecho.json())
