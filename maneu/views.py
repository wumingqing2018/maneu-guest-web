import requests
from django.shortcuts import render, HttpResponse


def index(request):
    return render(request, 'maneu/index.html')


def login(request):
    code = request.GET.get('code')
    url = 'https://api.weixin.qq.com/cgi-bin/token'
    data = {"appid": "wxf48b774de9be5613",
            "secret": "9a7ac5730b249c8ccc8a2b410631935b",
            "js_code": "1",
            "grant_type": "client_credential"
            }
    reecho = requests.get(url, data)
    print(reecho, reecho.json())
    url = 'https://api.weixin.qq.com/wxa/business/getuserphonenumber?access_token='+reecho.json()['access_token']
    print(url)
    data = {"code": '0e6d1f93fa99cd1909740b830ab561c7cacb061d947301d2bc2f595abef5008d'}
    reecho = requests.post(url=url, data=data)

    return HttpResponse(reecho, reecho.json())
