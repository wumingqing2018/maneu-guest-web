from pyexpat.errors import messages

from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkcore.client import AcsClient
from aliyunsdkdysmsapi.request.v20170525.SendSmsRequest import SendSmsRequest
import random, os, secrets, time,requests


def get_miniprogram_token():
    APPID = "wxf48b774de9be5613"
    APPSECRET = "e07b22bd5cac3c5a74baf9e03ffc7ce1"
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}"
    return requests.get(url).json()


def get_phone_number(code, data_token):
    url = f"https://api.weixin.qq.com/wxa/business/getuserphonenumber?access_token={data_token}"
    payload = {"code": code}
    response = requests.post(url, json=payload).json()
    if response['errcode'] == 0:
        return {'status': 200, 'message': response['phone_info']['phoneNumber']}
    elif response['errcode'] == 40001:
        return {'status': 401, 'message': response['errmsg']}
    elif response['errcode'] == 40029:
        return {'status': 429, 'message': response['errmsg']}
    else:
        return {'status': 500, 'message': response['errmsg']}
    return response  # 返回手机号


def current_time():
    """
    返回当前时间
    格式: Y-M-D H:M:S
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def getip(request):
    if request.META.get('HTTP_X_FORWARDED_FOR'):
        return request.META.get("HTTP_X_FORWARDED_FOR")
    else:
        return None


def randint():
    return random.randint(100000, 999999)


def generate_random_32hex():
    """生成32位随机十六进制字符串（安全加密级别）"""
    return secrets.token_hex(16)  # 16字节=32位十六进制


def sendsms(call, code):
    # Please ensure that the environment variables ALIBABA_CLOUD_ACCESS_KEY_ID and ALIBABA_CLOUD_ACCESS_KEY_SECRET are set.
    credentials = AccessKeyCredential(os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'],
                                      os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'])
    # use STS Token
    # credentials = StsTokenCredential(os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'], os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'], os.environ['ALIBABA_CLOUD_SECURITY_TOKEN'])
    client = AcsClient(region_id='cn-shenzhen', credential=credentials)

    request = SendSmsRequest()
    request.set_accept_format('json')
    request.set_SignName("爱视光学")
    request.set_TemplateCode("SMS_485420526")
    request.set_PhoneNumbers(call)
    request.set_TemplateParam({'code': code})

    response = client.do_action_with_exception(request)
    response = eval(response)
    return response
