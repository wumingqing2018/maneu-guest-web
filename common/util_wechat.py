
import logging
import os

import requests

logger = logging.getLogger(__name__)



# ============================================================================
# 一、微信小程序接口
# ============================================================================

def get_miniprogram_token():
    """
    调用微信接口获取 access_token。

    :return: 包含 access_token 和 expires_in 的字典，失败时返回空字典
    :rtype: dict
    :example:
        >>> get_miniprogram_token()
        {'access_token': 'xxx', 'expires_in': 7200}
    """
    wechat_app_id = os.environ.get('WECHAT_APP_ID')
    wechat_app_secret = os.environ.get('WECHAT_APP_SECRET')

    if not wechat_app_id or not wechat_app_secret:
        logger.error('微信 AppID 或 AppSecret 未配置')
        return {}

    url = (
        f"https://api.weixin.qq.com/cgi-bin/token"
        f"?grant_type=client_credential&appid={wechat_app_id}&secret={wechat_app_secret}"
    )
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if 'access_token' in data:
            return data
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
        >>> get_miniprogram_phone('code123', 'token456')
        {'status': True, 'message': '13800138000'}
        >>> get_miniprogram_phone('invalid', 'token')
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
            return {'status': False, 'message': '返回数据中无手机号'}
        return {'status': False, 'message': data.get('errmsg', '未知错误')}
    except requests.RequestException as e:
        logger.exception('请求微信手机号接口失败: %s', e)
        return {'status': False, 'message': '网络请求失败'}

