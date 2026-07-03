# -*- coding: utf-8 -*-
"""
通用工具函数模块
提供微信接口、时间、IP、随机数、短信发送等功能。
"""

import os
import time
import random
import secrets
import logging

import requests
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest

logger = logging.getLogger(__name__)

# ======================== 微信配置 ========================

WECHAT_APP_ID = os.environ.get('WECHAT_APP_ID')
WECHAT_APP_SECRET = os.environ.get('WECHAT_APP_SECRET')


# ======================== 微信接口 ========================

def get_miniprogram_token():
    """
    调用微信接口获取 access_token。

    请求微信服务器获取小程序全局唯一后台接口调用凭据。

    :return: 包含 access_token 和 expires_in 的字典，失败时返回空字典
    :rtype: dict
    :example:
        >>> get_miniprogram_token()
        {'access_token': 'xxx', 'expires_in': 7200}
    """
    if not WECHAT_APP_ID or not WECHAT_APP_SECRET:
        logger.error('微信 AppID 或 AppSecret 未配置')
        return {}
    url = (
        f"https://api.weixin.qq.com/cgi-bin/token"
        f"?grant_type=client_credential&appid={WECHAT_APP_ID}&secret={WECHAT_APP_SECRET}"
    )
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if 'access_token' in data:
            return data
        else:
            logger.error('微信返回异常: %s', data)
            return {}
    except requests.RequestException as e:
        logger.exception('请求微信 access_token 失败: %s', e)
        return {}


def get_miniprogram_phone(code, access_token):
    """
    通过微信 code 获取用户手机号。

    :param code: 小程序 wx.login 返回的临时凭证
    :type code: str
    :param access_token: 微信接口调用凭据
    :type access_token: str
    :return: 包含 status 和 message 的字典，成功时 message 为手机号字符串
    :rtype: dict
    :example:
        >>> get_phone_number('code123', 'token456')
        {'status': True, 'message': '13800138000'}
        >>> get_phone_number('invalid', 'token')
        {'status': False, 'message': 'invalid code'}
    """
    if not access_token:
        return {'status': False, 'message': 'access_token 为空'}

    url = f"https://api.weixin.qq.com/wxa/business/getuserphonenumber?access_token={access_token}"
    payload = {"code": code}
    try:
        resp = requests.post(url, json=payload, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if data.get('errcode') == 0:
            phone_number = data.get('phone_info', {}).get('phoneNumber')
            if phone_number:
                return {'status': True, 'message': phone_number}
            else:
                return {'status': False, 'message': '返回数据中无手机号'}
        else:
            return {'status': False, 'message': data.get('errmsg', '未知错误')}
    except requests.RequestException as e:
        logger.exception('请求微信手机号接口失败: %s', e)
        return {'status': False, 'message': '网络请求失败'}


# ======================== 时间工具 ========================

def current_time():
    """
    获取当前时间的字符串表示。

    :return: 格式为 'YYYY-MM-DD HH:MM:SS' 的时间字符串
    :rtype: str
    :example:
        >>> current_time()
        '2026-06-30 14:30:25'
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


# ======================== IP 获取 ========================

def getip(request):
    """
    从 Django 请求对象中获取客户端真实 IP 地址。

    优先从 HTTP_X_FORWARDED_FOR 获取（适用于反向代理），
    若不存在则使用 REMOTE_ADDR。

    :param request: Django HTTP 请求对象
    :type request: HttpRequest
    :return: IP 地址字符串，若无法获取则返回 None
    :rtype: str or None
    :example:
        >>> getip(request)
        '192.168.1.100'
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # 取第一个 IP（客户端真实 IP）
        ip = x_forwarded_for.split(',')[0].strip()
        return ip
    return request.META.get('REMOTE_ADDR')


# ======================== 随机数生成 ========================

def randint():
    """
    生成一个 6 位随机整数，用于短信验证码。

    :return: 100000 到 999999 之间的随机整数
    :rtype: int
    :example:
        >>> randint()
        482716
    """
    return random.randint(100000, 999999)


def generate_random_32hex():
    """
    生成 32 位随机十六进制字符串，安全级别高（适合令牌或密钥）。

    使用 secrets 模块，不可预测且适合加密用途。

    :return: 32 位十六进制字符串
    :rtype: str
    :example:
        >>> generate_random_32hex()
        'a1b2c3d4e5f678901234567890abcdef'
    """
    return secrets.token_hex(16)  # 16 字节 = 32 位十六进制


# ======================== 短信发送 ========================

def send_sms_code(call, code):
    """
    通过阿里云短信服务发送验证码。

    :param call: 接收短信的手机号
    :type call: str
    :param code: 6 位验证码（数字字符串或整数）
    :type code: str or int
    :return: 发送结果字典，包含 status (bool) 和 message (str)
    :rtype: dict
    :raises Exception: 阿里云 SDK 可能抛出的异常（已捕获并记录）

    :example:
        >>> send_sms_code('13800138000', '123456')
        {'status': True, 'message': 'OK'}
        >>> send_sms_code('invalid', '123456')
        {'status': False, 'message': 'Invalid phone number'}
    """
    # 读取阿里云密钥（必须从环境变量获取）
    access_key_id = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID')
    access_key_secret = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
    if not access_key_id or not access_key_secret:
        logger.error('阿里云 AccessKey 未配置（环境变量缺失）')
        return {'status': False, 'message': '系统配置错误，请检查密钥'}

    try:
        credentials = AccessKeyCredential(access_key_id, access_key_secret)
        client = AcsClient(region_id='cn-shenzhen', credential=credentials)

        request = SendSmsRequest()
        request.set_accept_format('json')
        request.set_SignName("爱视光学")           # 短信签名
        request.set_TemplateCode("SMS_485420526")  # 短信模板编码
        request.set_PhoneNumbers(call)
        request.set_TemplateParam({'code': str(code)})

        # 发送短信（返回 bytes）
        response_bytes = client.do_action_with_exception(request)
        response_str = response_bytes.decode('utf-8')
        result = eval(response_str)  # 转为字典

        if result.get('Code') == 'OK':
            return {'status': True, 'message': 'OK'}
        else:
            logger.warning('短信发送失败，阿里云返回: %s', result)
            return {'status': False, 'message': result.get('Message', '发送失败')}

    except Exception as e:
        logger.exception('短信发送异常: %s', e)
        return {'status': False, 'message': '系统繁忙，请稍后重试'}