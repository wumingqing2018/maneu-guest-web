"""
common/util_common.py
通用工具函数模块

提供：
    1. 微信小程序接口（access_token / 手机号）
    2. 阿里云短信发送
    3. 时间、IP、随机数等通用工具
    4. 正则格式校验（手机号 / 验证码 / UUID / 移动端 UA）
"""

import logging
import random
import secrets
import time

logger = logging.getLogger(__name__)


# ============================================================================
# 三、时间工具
# ============================================================================

def current_time():
    """
    获取当前时间的字符串表示。

    :return: 格式为 'YYYY-MM-DD HH:MM:SS' 的时间字符串
    :rtype: str
    :example:
        urrent_time()
        '2026-06-30 14:30:25'
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


# ============================================================================
# 四、IP 获取
# ============================================================================

def getip(request):
    """
    从 Django 请求对象中获取客户端真实 IP 地址。

    优先从 HTTP_X_FORWARDED_FOR 获取（适用于反向代理），
    若不存在则使用 REMOTE_ADDR。

    :param request: Django HTTP 请求对象
    :type request: HttpRequest
    :return: IP 地址字符串，若无法获取则返回 None
    :rtype: str or None
    :use:
        getip(request)
    :example:
        '192.168.1.100'
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # 取第一个 IP（客户端真实 IP）
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


# ============================================================================
# 五、随机数生成
# ============================================================================

def get_random_code():
    """
    生成一个 6 位随机整数，用于短信验证码。

    :return: 100000 到 999999 之间的随机整数
    :rtype: int
    :example:
        get_random_code()
        482711
    """
    return random.randint(100000, 999999)


def generate_random_32hex():
    """
    生成 32 位随机十六进制字符串，安全级别高（适合令牌或密钥）。

    使用 secrets 模块，不可预测且适合加密用途。

    :return: 32 位十六进制字符串
    :rtype: str
    :example:
        generate_random_32hex()
        'a1b2c3d4e5f678901234567890abcdef'
    """
    return secrets.token_hex(16)
