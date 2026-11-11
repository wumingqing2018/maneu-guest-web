"""
common/util_sms.py

阿里云短信发送封装。
- AcsClient 模块级单例，进程生命周期内复用
"""

import json
import logging
import os

from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkcore.client import AcsClient
from aliyunsdkdysmsapi.request.v20170525.SendSmsRequest import SendSmsRequest

logger = logging.getLogger(__name__)

# 模块级单例
_acs_client = None


def _get_client():
    """懒加载 AcsClient；首次调用时构造，后续复用。"""
    global _acs_client
    if _acs_client is None:
        credentials = AccessKeyCredential(
            os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID'),
            os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET'),
        )
        _acs_client = AcsClient(region_id='cn-shenzhen', credential=credentials)
    return _acs_client


def send_sms_code(call, code):
    """
    通过阿里云短信服务发送验证码。

    :param call: 接收短信的手机号
    :param code: 6 位验证码
    :return: {'status': bool, 'message': str}
    """
    try:
        request = SendSmsRequest()
        request.set_accept_format('json')
        request.set_SignName('爱视光学')
        request.set_TemplateCode('SMS_485420526')
        request.set_PhoneNumbers(call)
        request.set_TemplateParam({'code': str(code)})

        client = _get_client()
        response = client.do_action_with_exception(request)
        result = json.loads(response.decode('utf-8'))

        if result.get('Code') == 'OK':
            return {'status': True, 'message': 'OK'}

        logger.warning('短信发送失败，阿里云返回: %s', result)
        return {'status': False, 'message': result.get('Message', '发送失败')}

    except Exception as e:
        logger.exception('短信发送异常: %s', e)
        return {'status': False, 'message': '系统繁忙，请稍后重试'}
