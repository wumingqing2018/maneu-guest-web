import json
from django.http import JsonResponse
from django.shortcuts import render
from maneu.models import *

import os
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

def index(request):
    return render(request, 'index.html')


def login(request):
    if request.GET.get('call') == '' or request.GET.get('code') == '':
        content = {'status': False, 'message': 'call or code is none', 'data': {}}
    else:
        data = ManeuGuess.objects.filter(phone=request.GET.get('call')).first()
        content = {'status': True, 'message': 'success', 'content': {'call': data.phone, 'name': data.name, 'id': data.id}}
    return JsonResponse(content)


def get_list(request):
    if request.GET.get('code') == '':
        content = {'status': False, 'message': 'code is none', 'data': {}}
    else:
        if request.GET.get('text') == "Order":
            data = ManeuOrder.objects.filter(guess_id=request.GET.get('code')).order_by('-time').all().values('id', 'time')
            content = {'status': True, 'message': 'success', 'content': list(data)}
        elif request.GET.get('text') == "Service":
            data = ManeuService.objects.filter(guess_id=request.GET.get('code')).order_by('-time').all().values('id', 'time')
            content = {'status': True, 'message': 'success', 'content': list(data)}
        elif request.GET.get('text') == "Refraction":
            data = ManeuRefraction.objects.filter(guess_id=request.GET.get('code')).order_by('-time').all().values('id', 'time')
            content = {'status': True, 'message': 'success', 'content': list(data)}
        else:
            content = {'status': False, 'message': 'code is none', 'data': {}}
    return JsonResponse(content)


def get_detail(request):
    if request.GET.get('text') == "Order":
        try:
            order = ManeuOrderV2.objects.filter(id=request.GET.get('code')).first()
            store = ManeuStore.objects.filter(id=order.store_id).first()
            vision = ManeuVision.objects.filter(id=order.vision_id).first()
            content = {'status': True,
                       'message': 'success',
                       'time': order.time,
                       'store': json.loads(store.content),
                       'vision': json.loads(vision.content)}
        except Exception as e:
            content = {'status': False, 'message': e}
    elif request.GET.get('text') == "Service":
        try:
            data = ManeuService.objects.filter(guess_id=request.GET.get('code')).order_by('-time').first().values('time', 'content')
            content = {'status': True, 'message': 'success', 'content': list(data)}
        except Exception as e:
            content = {'status': False, 'message': e}
    elif request.GET.get('text') == "Refraction":
        try:
            data = json.loads(ManeuRefraction.objects.filter(id=request.GET.get('code')).first().content)
            content = {'status': True, 'message': 'success', 'content': data}
        except Exception as e:
            content = {'status': False, 'message': e}
    else:
        content = {'status': False, 'message': 'code is none'}
    return JsonResponse(content)


def sendSMS(request):
    # 创建AcsClient实例，需替换为您自己的AccessKey信息
    ACCESS_KEY_ID = 'LTAI5tCTtBTqsjYnsgHHGt8H'  # 在阿里云控制台创建AccessKey时自动生成的一对访问密钥，上面保存的AccessKey
    ACCESS_KEY_SECRET = '1lMUPjj2tOi9c1OyNpCOrsbNhmWrZQ'  # 在阿里云控制台创建AccessKey时自动生成的一对访问密钥AccessKey
    SIGN_NAME = '徕可'  # 短信签名
    template_code = 'maneu'  # 短信模板CODE
    PhoneNumber = '13268651582'  # 绑定的测试手机号
    acs_client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, template_code)

    # 创建CommonRequest实例
    request = CommonRequest()

    # 设置请求参数,下面这5行其实不用动
    request.set_accept_format('json')  # 设置API响应格式的方法
    request.set_domain('dysmsapi.aliyuncs.com')  # 设置API的域名的方法
    request.set_method('POST')  # 设置API请求方法
    request.set_version('2017-05-25')  # 设置API版本号
    request.set_action_name('SendSms')  # 设置API操作名

    # 设置短信模板参数
    request.add_query_param('PhoneNumbers', PhoneNumber)
    request.add_query_param('SignName', SIGN_NAME)
    request.add_query_param('TemplateCode', template_code)
    request.add_query_param('TemplateParam', '{"code":"123456"}')

    # 发送短信请求并获取返回结果
    response = acs_client.do_action_with_exception(request)

    print(response)
