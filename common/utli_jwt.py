from datetime import datetime, timedelta

import jwt
from django.conf import settings

from common.verify import is_uuid

JWT_SECRET = settings.JWT_CONFIG['SECRET_KEY']
JWT_ALGORITHM = settings.JWT_CONFIG['ALGORITHM']
ACCESS_LIFETIME = settings.JWT_CONFIG['ACCESS_TOKEN_LIFETIME']       # 3600
REFRESH_LIFETIME = settings.JWT_CONFIG.get('REFRESH_TOKEN_LIFETIME', 604800)  # 7天


def generate_access_token(user):
    """生成 Access Token"""
    payload = {
        'user_id': str(user.id),
        'type': 'access',
        'exp': datetime.utcnow() + timedelta(seconds=ACCESS_LIFETIME),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def generate_refresh_token(user):
    """生成 Refresh Token（无状态 JWT，type 为 refresh）"""
    payload = {
        'user_id': str(user.id),
        'type': 'refresh',
        'exp': datetime.utcnow() + timedelta(seconds=REFRESH_LIFETIME),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token, expected_type=None):
    """
    验证 JWT，成功返回 payload，失败返回 None。
    expected_type: 'access' 或 'refresh'，用于限制 token 用途。
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if expected_type and payload.get('type') != expected_type:
            return None
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def _get_admin_id(request):
    """
    从请求中获取管理员ID（JWT优先，兼容session）
    """
    # 优先使用JWT注入的id（由中间件处理）
    admin_id = getattr(request, 'jwt_user_id', None)
    if admin_id and is_uuid(admin_id):
        return admin_id
    return None
