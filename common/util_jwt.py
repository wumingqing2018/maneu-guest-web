"""
common/util_jwt.py
你可以这个注释段落添加注释，方便下次检查优化及记录

JWT 工具模块
职责：生成、解码、拉黑、黑名单查询、辅助读取 request
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


def _now():
    return datetime.now(timezone.utc)


def _base_payload(user, token_type, lifetime_seconds):
    """构造基础 payload：同时携带 user_id 和 user_phone"""
    now = _now()
    return {
        'user_id': str(user.id),
        'user_phone': getattr(user, 'phone', None),  # ← 业务用手机号
        'type': token_type,
        'jti': str(uuid.uuid4()),
        'iss': JWT_ISSUER,
        'iat': now,
        'exp': now + timedelta(seconds=lifetime_seconds),
    }


def generate_access_token(user):
    payload = _base_payload(user, 'access', ACCESS_LIFETIME)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def generate_refresh_token(user):
    payload = _base_payload(user, 'refresh', REFRESH_LIFETIME)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def generate_token_pair(user):
    return {
        'access_token': generate_access_token(user),
        'refresh_token': generate_refresh_token(user),
        'expires_in': ACCESS_LIFETIME,
    }


def decode_token(token, expected_type=None):
    """解码并校验，失败抛 jwt 异常"""
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
    """
    兼容旧调用：成功返回 payload，失败返回 None（不抛异常）
    """
    try:
        return decode_token(token, expected_type=expected_type)
    except jwt.PyJWTError:
        return None


def blacklist_token(payload):
    jti = payload.get('jti')
    exp = payload.get('exp')
    if not jti or not exp:
        return
    exp_ts = int(exp.timestamp()) if isinstance(exp, datetime) else int(exp)
    ttl = exp_ts - int(_now().timestamp())
    if ttl > 0:
        cache.set(f'{BLACKLIST_PREFIX}{jti}', 1, timeout=ttl)


def is_blacklisted(payload):
    jti = payload.get('jti')
    return bool(jti and cache.get(f'{BLACKLIST_PREFIX}{jti}'))


# ========================= 辅助：从 request 读用户信息 =========================

def get_admin_phone_from_request(request):
    """从中间件挂载的 request 取手机号"""
    return getattr(request, 'jwt_phone', None)


def get_admin_id_from_request(request):
    """从中间件挂载的 request 取 user_id"""
    return getattr(request, 'jwt_user_id', None)
