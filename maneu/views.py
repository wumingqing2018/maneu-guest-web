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
