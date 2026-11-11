"""
common/util_common.py

通用工具：时间 / IP / 随机字符串。

相关模块：
    - 微信接口      → util_wechat.py
    - 阿里云短信    → util_sms.py
    - 正则格式校验  → util_verify.py
    - 短信验证码    → service.generate_sms_code（唯一来源，勿在此重复实现）
"""

import logging
import secrets
import time

logger = logging.getLogger(__name__)


# ============================================================================
# 一、时间
# ============================================================================

def current_time():
    """当前时间字符串：'YYYY-MM-DD HH:MM:SS'。"""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


# ============================================================================
# 二、IP
# ============================================================================

def getip(request):
    """
    从 Django 请求中获取客户端 IP。

    ⚠️ X-Forwarded-For 可被客户端伪造，仅当服务前有可信反向代理时使用；
       无代理时请改用 REMOTE_ADDR。

    :param request: Django HttpRequest
    :return: IP 字符串；无法获取时返回 None
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


# ============================================================================
# 三、随机字符串
# ============================================================================

def generate_random_32hex():
    """
    生成 32 位随机十六进制字符串（secrets 级，适合作为令牌/密钥）。
    使用 secrets 模块，不可预测。
    """
    return secrets.token_hex(16)
