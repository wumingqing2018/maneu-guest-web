import json

from django.http import JsonResponse
from django.shortcuts import render

from maneu.models import *


def index(request):
    return render(request, 'index.html')


def login(request):
    if request.GET.get('call') == '' or request.GET.get('code') == '':
        content = {'status': False, 'message': 'call or code is none', 'data': {}}
    else:
        data = ManeuGuess.objects.filter(phone=request.GET.get('call')).first()
        content = {'status': True, 'message': 'success',
                   'content': {'call': data.phone, 'name': data.name, 'id': data.id}}
    return JsonResponse(content)


def get_list(request):
    if request.GET.get('code') == '':
        content = {'status': False, 'message': 'code is none', 'data': {}}
    else:
        if request.GET.get('text') == "Order":
            data = ManeuOrder.objects.filter(guess_id=request.GET.get('code')).order_by('-time').all().values('id',
                                                                                                              'time')
            content = {'status': True, 'message': 'success', 'content': list(data)}
        elif request.GET.get('text') == "Service":
            data = ManeuService.objects.filter(guess_id=request.GET.get('code')).order_by('-time').all().values('id',
                                                                                                                'time')
            content = {'status': True, 'message': 'success', 'content': list(data)}
        elif request.GET.get('text') == "Refraction":
            data = ManeuRefraction.objects.filter(guess_id=request.GET.get('code')).order_by('-time').all().values('id',
                                                                                                                   'time')
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
            data = ManeuService.objects.filter(guess_id=request.GET.get('code')).order_by('-time').first().values(
                'time', 'content')
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
