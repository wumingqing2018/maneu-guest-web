import json
import uuid

from django.forms.models import model_to_dict
from django.shortcuts import render

from common import common
from common import verify_util
from maneu.models import *


def index(request):
    index_id = request.GET.get('index_id')
    return render(request, 'index.html', {'index_id': index_id})


def verify_order(request):
    index_id = request.GET.get('index_id')
    return render(request, 'order.html', {'index_id': index_id})


def verify_store(request):
    index_id = request.GET.get('index_id')
    return render(request, 'store.html', {'index_id': index_id})


def verify_report(request):
    index_id = request.GET.get('index_id')
    return render(request, 'report.html', {'index_id': index_id})


def login(request):
    call = verify_util.is_call(request.GET.get('call'))
    code = verify_util.is_code(request.GET.get('code'))

    if call and code:
        token = uuid.uuid4()
        guest = ManeuGuest.objects.filter(phone=call).all().update(remark=token)
        if guest:
            content = {'status': True, 'message': '请求成功', 'content': {}, 'token': token}
        else:
            content = {'status': False, 'message': '请求失败', 'content': {}, 'token': ''}
    else:
        content = {'status': False, 'message': '登录失败：请提交正确的手机号和验证码', 'content': {}, 'token': ''}

    return JsonResponse(content)


def login_wx(request):
    code = verify_util.is_token2(request.GET.get('code'))
    if code:
        data_token = ManeuAdmin.objects.filter().first()
        phone = common.get_phone_number(code, data_token.content)
        if phone['status']:
            token = uuid.uuid4()
            guest = ManeuGuest.objects.filter(phone=phone['message']).update(remark=token)
            if guest != 0:
                content = {'status': True, 'message': '请求成功', 'content': {}, 'token': token}
            else:
                content = {'status': False, 'message': '请求失败', 'content': {}, 'token': ''}
        else:
            data_token = common.get_miniprogram_token()['access_token']
            ManeuAdmin.objects.all().update(content=data_token)
            phone = common.get_phone_number(code, data_token)
            if phone['status']:
                token = uuid.uuid4()
                guest = ManeuGuest.objects.filter(phone=phone['message']).update(remark=token)
                if guest != 0:
                    content = {'status': True, 'message': '请求成功', 'content': {}, 'token': token}
                else:
                    content = {'status': False, 'message': '请求失败', 'content': {}, 'token': ''}
            else:
                content = {'status': False, 'message': '请求失败：请联系管理员', 'content': {}, 'token': ''}
    else:
        content = {'status': False, 'message': '登录失败：请提交正确的微信号', 'content': {}, 'token': ''}

    return JsonResponse(content)



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from common.sendSMSForm import SendSMSForm

@csrf_exempt  # 因为使用 JWT，无需 CSRF
@require_http_methods(["POST"])  # 只允许 POST
def sendsms(request):
    form = SendSMSForm(request.POST)
    if form.is_valid():
        call = form.cleaned_data['call']
        code = form.cleaned_data['code']  # 由表单 clean 生成的验证码

        # 调用短信发送服务
        response = common.sendsms(call=call, code=code)
        if response.get('Code') == 'OK':
            content = {'status': True,'message': '验证码已发送', 'content': {}}
        else:
            content = {'status': False, 'message': response["Message"], 'content': {}}
    else:
        content = {'status': False, 'message': form.errors.as_text(), 'content': {}}
    return JsonResponse(content)

def sendsms(request):
    call = verify_util.is_call(request.GET.get('code'))
    if call:
        code = common.randint()
        data = ManeuGuest.objects.filter(phone=call).all().update(remark=code)
        if data:
            response = common.sendsms(call, code)
            if response['Code'] == 'OK':
                content = {'status': True, 'message': '请求成功', 'content': {}, 'token': ''}
            else:
                content = {'status': False, 'message': '短信发送失败，今日次数用完了', 'content': {}, 'token': ''}
        else:
            content = {'status': False, 'message': '请求失败', 'content': {}, 'token': ''}
    else:
        content = {'status': False, 'message': '登录失败：请提交正确的手机号', 'content': {}, 'token': ''}
    return JsonResponse(content)


def get_index(request):
    data = [{
        "index": 'https://maneu.online/static/img/3.gif',
        "data": 'https://maneu.online/static/img/gif2.jpg',
    }, {
        "index": 'https://maneu.online/static/img/1mcjs.jpg',
        "data": 'https://maneu.online/static/img/2mcjs.jpg',
    }, {
        "index": 'https://maneu.online/static/img/1xzy.jpg',
        "data": 'https://maneu.online/static/img/2xzy.jpg',
    }, {
        "index": 'https://maneu.online/static/img/1yqs.jpg',
        "data": 'https://maneu.online/static/img/2yqs.jpg',
    }, {
        "index": 'https://maneu.online/static/img/1njj.jpg',
        "data": 'https://maneu.online/static/img/2njj.jpg',
    }]
    return JsonResponse({'status': True, 'message': '', 'content': data})


def get_list(request):
    text = verify_util.is_code(request.GET.get('text'))
    token = verify_util.is_uuid(request.GET.get('token'))

    guest = ManeuGuest.objects.filter(remark=token).first()
    if guest:
        remark = str(uuid.uuid4())
        guest_update = ManeuGuest.objects.filter(remark=token).update(remark=remark)

        if text == "100001":
            data = ManeuOrder.objects.filter(phone=guest.phone, status=3).order_by('-time').all().values('id', 'name', 'time', 'phone', 'remark')
            return JsonResponse({'status': True, 'message': '', 'content': list(data), 'token': remark})
        elif text == "100002":
            data = ManeuReport.objects.filter(phone=guest.phone, status=2).order_by('-time').all().values('id', 'name', 'time', 'phone', 'remark')
            return JsonResponse({'status': True, 'message': '', 'content': list(data), 'token': remark})
        elif text == "100003":
            data = ManeuRepair.objects.filter(phone=guest.phone).order_by('-time').all().values('id', 'name', 'time', 'phone', 'remark')
            return JsonResponse({'status': True, 'message': '', 'content': list(data), 'token': remark})
        else:
            content = {'status': False, 'message': 'text is wrong' + request.GET.get('text'), 'content': {}, 'token': ''}
    else:
        content = {'status': False, 'message': 'mark is wrong' + request.GET.get('token'), 'content': {}, 'token': ''}

    return JsonResponse(content)


def get_detail(request):
    code = verify_util.is_uuid(request.GET.get('code'))
    text = verify_util.is_code(request.GET.get('text'))
    token = verify_util.is_uuid(request.GET.get('token'))

    if text:
        if code:
            guest = ManeuGuest.objects.filter(remark=token).first()
            if guest:
                remark = uuid.uuid4()
                guest1 = ManeuGuest.objects.filter(remark=token).update(remark=remark)
                if request.GET.get('text') == "100001":
                    try:
                        data = ManeuOrder.objects.filter(id=code).first()
                        content = {'status': True, 'message': '请求成功', 'content': model_to_dict(data), 'token': remark}
                    except Exception as e:
                        content = {'status': False, 'message': str(e), 'content': {}, 'token': remark}
                elif request.GET.get('text') == "100002":
                    try:
                        store = ManeuStore.objects.filter(id=code).first()
                        content = {'status': True, 'message': '请求成功', 'content': json.loads(store.content), 'token': remark}
                    except Exception as e:
                        content = {'status': False, 'message': str(e), 'content': {}, 'token': remark}
                elif request.GET.get('text') == "100003":
                    try:
                        data = ManeuReport.objects.filter(id=code).first()
                        content = {'status': True, 'message': '请求成功', 'content': model_to_dict(data), 'token': remark}
                    except Exception as e:
                        content = {'status': False, 'message': str(e), 'content': {}, 'token': remark}
                elif request.GET.get('text') == "100004":
                    try:
                        data = ManeuGuest.objects.filter(id=code).first()
                        content = {'status': True, 'message': '请求成功', 'content': model_to_dict(data), 'token': remark}
                    except Exception as e:
                        content = {'status': False, 'message': str(e), 'content': {}, 'token': remark}
                elif request.GET.get('text') == "100005":
                    try:
                        data = ManeuAdmin.objects.filter(id=code).first()
                        content = {'status': True, 'message': '请求成功', 'content': model_to_dict(data), 'token': remark}
                    except Exception as e:
                        content = {'status': False, 'message': str(e), 'content': {}, 'token': remark}
                elif request.GET.get('text') == "100006":
                    try:
                        data = ManeuRepair.objects.filter(guest_id=code).first()
                        content = {'status': True, 'message': '请求成功', 'content': model_to_dict(data), 'token': remark}
                    except Exception as e:
                        content = {'status': False, 'message': str(e), 'content': {}, 'token': remark}
                elif request.GET.get('text') == "100007":
                    try:
                        ManeuVerify.objects.create(order_id=code, guest_id=guest.id, name=guest.name, call=guest.phone, time=common.current_time())
                        data = ManeuVerify.objects.filter(order_id=code).order_by('-time').all().values('time')
                        content = {'status': True, 'message': '请求成功', 'content': list(data), 'token': remark}
                    except Exception as e:
                        content = {'status': False, 'message': str(e), 'content': {}, 'token': remark}
                else:
                    content = {'status': False, 'message': 'text is wrong' + str(request.GET.get('text')), 'content': {}, 'token': ''}
            else:
                content = {'status': False, 'message': 'mark is wrong' + str(request.GET.get('token')), 'content': {}, 'token': ''}
        else:
            content = {'status': False, 'message': 'code is wrong' + str(request.GET.get('code')), 'content': {}, 'token': ''}
    else:
        content = {'status': False, 'message': 'text is wrong' + str(request.GET.get('text')), 'content': {}, 'token': ''}

    return JsonResponse(content)