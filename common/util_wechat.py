"""
common/util_wechat.py

微信小程序接口封装：access_token / openid / 手机号 / 域名校验文件。

token 缓存策略：
    写入 Redis 时 TTL = 7200 - 300 秒，提前 300 秒过期避开边界。
    force_refresh=True 用于 token 失效重试，跳过缓存直接刷新。
"""

import logging
import os

import requests
from django.core.cache import cache

logger = logging.getLogger(__name__)

# 微信 token 有效期 7200s，提前 300s 过期避开边界
_TOKEN_CACHE_KEY = 'wechat:miniprogram:access_token'
_TOKEN_CACHE_TTL = 7200 - 300


def _get_app_credentials():
    """读取 AppID / AppSecret，缺一返回 (None, None)"""
    return (
        os.environ.get('WECHAT_APP_ID'),
        os.environ.get('WECHAT_APP_SECRET'),
    )


# ============================================================================
# 一、access_token
# ============================================================================

def get_miniprogram_token(force_refresh=False):
    """
    获取微信 access_token。

    :param force_refresh: True 时跳过缓存强制刷新
    :return: {'access_token': str, 'expires_in': int}，失败返回 {}
    """
    if not force_refresh:
        cached = cache.get(_TOKEN_CACHE_KEY)
        if cached:
            return {'access_token': cached, 'expires_in': _TOKEN_CACHE_TTL}

    app_id, app_secret = _get_app_credentials()
    if not app_id or not app_secret:
        logger.error('微信 AppID 或 AppSecret 未配置')
        return {}

    url = (
        'https://api.weixin.qq.com/cgi-bin/token'
        f'?grant_type=client_credential&appid={app_id}&secret={app_secret}'
    )
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        logger.exception('请求微信 access_token 失败: %s', e)
        return {}

    token = data.get('access_token')
    if not token:
        logger.error('微信返回异常: %s', data)
        return {}

    cache.set(_TOKEN_CACHE_KEY, token, timeout=_TOKEN_CACHE_TTL)
    return data


# ============================================================================
# 二、openid
# ============================================================================

def get_miniprogram_open_id(login_code):
    """
    用 wx.login() 的 code 换 openid。

    ⚠️ 这是唯一能拿到 openid 的方式，前端永远拿不到。
    code 5 分钟有效、仅能使用一次；重复使用微信返回 40163。

    :param login_code: wx.login() 返回的临时 code
    :return: openid 字符串；失败返回 None
    """
    if not login_code:
        return None

    app_id, app_secret = _get_app_credentials()
    if not app_id or not app_secret:
        logger.error('微信 AppID 或 AppSecret 未配置')
        return None

    url = 'https://api.weixin.qq.com/sns/jscode2session'
    params = {
        'appid': app_id,
        'secret': app_secret,
        'js_code': login_code,
        'grant_type': 'authorization_code',
    }
    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        logger.exception('jscode2session 请求失败: %s', e)
        return None

    openid = data.get('openid')
    if openid:
        return openid

    # 常见错误：40029 code 无效；40163 code 已被使用；45011 频率限制
    logger.warning('jscode2session 返回异常: %s', data)
    return None


# ============================================================================
# 三、手机号
# ============================================================================

def get_miniprogram_phone(code, access_token):
    """
    通过手机号快速验证的 code 换取手机号。

    ⚠️ 这里的 code 来自 <button open-type="getPhoneNumber"> 回调，
       不是 wx.login 的 code，两者不能混用。

    :param code: 手机号快速验证 code
    :param access_token: 微信接口调用凭据
    :return: {'status': bool, 'message': 手机号 or 错误信息}
    """
    if not access_token:
        return {'status': False, 'message': 'access_token 为空'}

    url = (
        'https://api.weixin.qq.com/wxa/business/getuserphonenumber'
        f'?access_token={access_token}'
    )
    try:
        resp = requests.post(url, json={'code': code}, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        logger.exception('请求微信手机号接口失败: %s', e)
        return {'status': False, 'message': '网络请求失败'}

    if data.get('errcode') != 0:
        return {'status': False, 'message': data.get('errmsg', '未知错误')}

    phone_number = data.get('phone_info', {}).get('phoneNumber')
    if not phone_number:
        return {'status': False, 'message': '返回数据中无手机号'}
    return {'status': True, 'message': phone_number}


# ============================================================================
# 四、域名校验文件
# ============================================================================

def get_file_verify_content():
    """
    微信域名校验文件内容（读取环境变量 WECHAT_FILE_VERIFY）。
    未配置时返回空字符串，避免 HttpResponse(None) 报错。
    """
    return os.environ.get('WECHAT_FILE_VERIFY') or ''
