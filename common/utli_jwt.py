from datetime import timedelta
from typing import Optional, Any

import jwt
from django.conf import settings
from django.utils import timezone

from common.util_verify import is_call


# ---------- JWT 配置（从 settings 读取，带默认值） ----------
JWT_CONFIG = getattr(settings, 'JWT_CONFIG', {})
JWT_SECRET = JWT_CONFIG.get('SECRET_KEY')
JWT_ALGORITHM = JWT_CONFIG.get('ALGORITHM', 'HS256')
ACCESS_LIFETIME = JWT_CONFIG.get('ACCESS_TOKEN_LIFETIME', 3600)          # 默认 1 小时
REFRESH_LIFETIME = JWT_CONFIG.get('REFRESH_TOKEN_LIFETIME', 604800)      # 默认 7 天


def generate_access_token(user) -> str:
    """
    生成用于身份认证的 Access Token。

    Args:
        user: Django User 模型实例，必须包含 `phone` 属性（通常为手机号码）。

    Returns:
        str: JWT 编码的字符串。

    Note:
        Token 中存放 `user_phone`（字符串形式），以便中间件解析并挂载到 `request.jwt_user_phone`。
        过期时间由 `ACCESS_LIFETIME` 控制。
    """
    payload = {
        'user_phone': str(user.phone),           # 统一使用 user.phone，不再使用 phone
        'type': 'access',
        'exp': timezone.now() + timedelta(seconds=ACCESS_LIFETIME),
        'iat': timezone.now(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def generate_refresh_token(user) -> str:
    """
    生成用于刷新 Access Token 的 Refresh Token。

    Args:
        user: Django User 模型实例，必须包含 `phone` 属性。

    Returns:
        str: JWT 编码的字符串。

    Note:
        Refresh Token 本身也是无状态 JWT，类型标记为 'refresh'。
        过期时间由 `REFRESH_LIFETIME` 控制，通常比 Access Token 更长。
    """
    payload = {
        'user_phone': str(user.phone),
        'type': 'refresh',
        'exp': timezone.now() + timedelta(seconds=REFRESH_LIFETIME),
        'iat': timezone.now(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str, expected_type: Optional[str] = None) -> Optional[dict]:
    """
    验证 JWT 并返回解码后的 payload。

    Args:
        token: JWT 字符串。
        expected_type: 可选，限制 token 的用途，如 'access' 或 'refresh'。
                      若指定，则 token 中的 'type' 必须与之匹配。

    Returns:
        Optional[dict]: 验证成功时返回 payload 字典，否则返回 None。

    Note:
        该方法会捕获所有 JWT 解码异常（过期、无效签名等），统一返回 None。
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if expected_type and payload.get('type') != expected_type:
            return None
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def get_admin_phone_from_request(request) -> Optional[str]:
    """
    从请求对象中提取管理员 phone（JWT 注入的 `jwt_user_phone`）。

    Args:
        request: Django HttpRequest 对象，中间件会在其上注入 `jwt_user_phone` 属性。

    Returns:
        Optional[str]: 如果存在且为有效的 UUphone 格式，则返回该 phone；否则返回 None。

    Note:
        该函数专门用于需要 UUphone 格式管理员 phone 的场景。
        若您的项目使用整数自增 phone，请移除 `is_uuphone` 校验或改用其他校验逻辑。
    """
    user_phone = getattr(request, 'jwt_user_phone', None)
    if user_phone and is_call(user_phone):
        return user_phone
    return None
