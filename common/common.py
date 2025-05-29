from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkcore.client import AcsClient
from aliyunsdkdysmsapi.request.v20170525.SendSmsRequest import SendSmsRequest
import random, os, secrets


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
