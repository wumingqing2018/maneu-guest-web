"""
common/util_jwt.py

JWT 工具模块。

职责：
    1. 生成 access / refresh token
    2. 解码 + 类型校验
    3. 按 jti 拉黑 / 查询黑名单（Redis，TTL = 剩余有效期）

约定：
    - payload 携带 user_id（UUID）与 user_phone（业务手机号）
    - 用户信息以 user_id 为准；user_phone 仅辅助展示
    - token 类型分为 'access' / 'refresh'，decode 时显式校验
    - 黑名单 key：jwt:blacklist:{jti}，值 1，过期时间与 token 剩余时间一致
"""

import uuid
from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings
from django.core.cache import cache

JWT_CONFIG = settings.JWT_CONFIG
JWT_SECRET = JWT_CONFIG['SECRET_KEY']
JWT_ALGORITHM = JWT_CONFIG['ALGORITHM']
JWT_ISSUER = JWT_CONFIG.get('ISSUER', 'maneu')
ACCESS_LIFETIME = JWT_CONFIG['ACCESS_TOKEN_LIFETIME']
REFRESH_LIFETIME = JWT_CONFIG.get('REFRESH_TOKEN_LIFETIME', 60 * 60 * 24 * 7)

BLACKLIST_PREFIX = 'jwt:blacklist:'


# ============================================================================
# 内部辅助
# ============================================================================

def _now():
    return datetime.now(timezone.utc)


def _base_payload(user, token_type, lifetime_seconds):
    """构造基础 payload：同时携带 user_id 和 user_phone"""
    now = _now()
    return {
        'user_id': str(user.id),
        'user_phone': getattr(user, 'phone', None),
        'type': token_type,
        'jti': str(uuid.uuid4()),
        'iss': JWT_ISSUER,
        'iat': now,
        'exp': now + timedelta(seconds=lifetime_seconds),
    }


# ============================================================================
# 一、生成
# ============================================================================

def generate_access_token(user):
    """生成 access token"""
    payload = _base_payload(user, 'access', ACCESS_LIFETIME)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def generate_refresh_token(user):
    """生成 refresh token"""
    payload = _base_payload(user, 'refresh', REFRESH_LIFETIME)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def generate_token_pair(user):
    """同时生成 access / refresh，供登录接口直接返回"""
    return {
        'access_token': generate_access_token(user),
        'refresh_token': generate_refresh_token(user),
        'expires_in': ACCESS_LIFETIME,
    }


# ============================================================================
# 二、解码
# ============================================================================

def decode_token(token, expected_type=None):
    """
    解码并校验：签名 / 算法 / issuer / 类型。
    失败抛 jwt 异常（ExpiredSignatureError / InvalidTokenError）。
    """
    payload = jwt.decode(
        token,
        JWT_SECRET,
        algorithms=[JWT_ALGORITHM],
        issuer=JWT_ISSUER,
    )
    if expected_type and payload.get('type') != expected_type:
        raise jwt.InvalidTokenError('Token 类型错误')
    return payload


def verify_token(token, expected_type=None):
    """兼容旧调用：成功返回 payload，失败返回 None（不抛异常）"""
    try:
        return decode_token(token, expected_type=expected_type)
    except jwt.PyJWTError:
        return None


# ============================================================================
# 三、黑名单
# ============================================================================

def blacklist_token(payload):
    """按 jti 拉黑；TTL 设为 token 剩余有效期，过期后自动清理"""
    jti = payload.get('jti')
    exp = payload.get('exp')
    if not jti or not exp:
        return
    exp_ts = int(exp.timestamp()) if isinstance(exp, datetime) else int(exp)
    ttl = exp_ts - int(_now().timestamp())
    if ttl > 0:
        cache.set(f'{BLACKLIST_PREFIX}{jti}', 1, timeout=ttl)


def is_blacklisted(payload):
    """判断 jti 是否已在黑名单"""
    jti = payload.get('jti')
    return bool(jti and cache.get(f'{BLACKLIST_PREFIX}{jti}'))


# ============================================================================
# 四、从 request 读取用户信息（中间件挂载后使用）
# ============================================================================

def get_admin_phone_from_request(request):
    """中间件挂载的手机号"""
    return getattr(request, 'jwt_phone', None)


def get_admin_id_from_request(request):
    """中间件挂载的 user_id"""
    return getattr(request, 'jwt_user_id', None)
