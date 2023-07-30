import requests
from django.shortcuts import render


def index(request):
    return render(request, 'maneu/index.html')


def login(request):
    url = 'https://api.weixin.qq.com/cgi-bin/token'
    data = {"appid": "wxf48b774de9be5613",
            "secret": "9a7ac5730b249c8ccc8a2b410631935b",
            "js_code": "1",
            "grant_type": "client_credential"
            }
    reecho = requests.get(url, data)
    print(reecho, reecho.json())
    url = 'https://api.weixin.qq.com/wxa/business/getuserphonenumber'
    data = {"access_token": reecho.json()['access_token'],
            "code": '71ca38341d563926eca5bd62348211b1c770b64d105717d2bcf89e345c8a9d36'}
    reecho = requests.post(url=url, data=data)
    print(reecho, reecho.json())

    return render(request, 'maneu/index.html')
