
import json
import logging
import os

from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkcore.client import AcsClient
from aliyunsdkdysmsapi.request.v20170525.SendSmsRequest import SendSmsRequest

logger = logging.getLogger(__name__)

# ============================================================================
# 二、阿里云短信
# ============================================================================

def send_sms_code(call, code):
    """
    通过阿里云短信服务发送验证码。

    :param call: 接收短信的手机号
    :type call: str
    :param code: 6 位验证码（数字字符串或整数）
    :type code: str or int
    :return: 发送结果字典，包含 status (bool) 和 message (str)
    :rtype: dict
    :use:
         send_sms_code('13800138000', '123456')
    :example:
        {'status': True, 'message': 'OK'}
        or
        {'status': False, 'message': 'Invalid phone number'}
    """
    try:
        credentials = AccessKeyCredential(
            os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID'),
            os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET'),
        )
        request = SendSmsRequest()
        request.set_accept_format('json')
        request.set_SignName("爱视光学")
        request.set_TemplateCode("SMS_485420526")
        request.set_PhoneNumbers(call)
        request.set_TemplateParam({'code': code})

        client = AcsClient(region_id='cn-shenzhen', credential=credentials)
        response = client.do_action_with_exception(request)

        result = json.loads(response.decode('utf-8'))

        if result.get('Code') == 'OK':
            return {'status': True, 'message': 'OK'}

        logger.warning('短信发送失败，阿里云返回: %s', result)
        return {'status': False, 'message': result.get('Message', '发送失败')}

    except Exception as e:
        logger.exception('短信发送异常: %s', e)
        return {'status': False, 'message': '系统繁忙，请稍后重试'}

