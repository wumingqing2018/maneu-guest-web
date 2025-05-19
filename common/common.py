from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkcore.client import AcsClient
from aliyunsdkdysmsapi.request.v20170525.SendSmsRequest import SendSmsRequest
import random, os

def randint():
    return random.randint(100000, 999999)

def sendsms(call, code):
    # Please ensure that the environment variables ALIBABA_CLOUD_ACCESS_KEY_ID and ALIBABA_CLOUD_ACCESS_KEY_SECRET are set.
    credentials = AccessKeyCredential(os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'],
                                      os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'])
    # use STS Token
    # credentials = StsTokenCredential(os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'], os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'], os.environ['ALIBABA_CLOUD_SECURITY_TOKEN'])
    client = AcsClient(region_id='cn-shenzhen', credential=credentials)

    request = SendSmsRequest()
    request.set_accept_format('json')
    request.set_SignName("徕可")
    request.set_TemplateCode("SMS_471990239")
    request.set_PhoneNumbers(call)
    request.set_TemplateParam({'code': code})

    response = client.do_action_with_exception(request)
    response = eval(response)
    return response
