"""
common/UserMiddleware.py

JWT 鉴权中间件。

规则：
    路径含 AUTH_URL_KEYWORDS（默认 '/auth/'）→ 需鉴权
    其他路径 → 直接放行

流程：
    1. 取 Authorization 头 → 提取 Bearer token
    2. 解码 + 校验类型 / 签名 / issuer
    3. 校验黑名单（jti 是否已失效）
    4. 挂载到 request：jwt_user_id / jwt_phone / jwt_payload
"""

import jwt
from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from common.util_jwt import decode_token, is_blacklisted

JWT_CONFIG = settings.JWT_CONFIG

# 需要鉴权的路径关键词
AUTH_URL_KEYWORDS = JWT_CONFIG.get('AUTH_URL_KEYWORDS', ['/auth/'])

# Authorization 头 META 键名
AUTH_HEADER_NAME = JWT_CONFIG.get('AUTH_HEADER_NAME', 'HTTP_AUTHORIZATION')

# 鉴权前缀（默认 'Bearer '），支持 settings 覆盖多种类型时取第一个
_AUTH_TYPES = JWT_CONFIG.get('AUTH_HEADER_TYPES', ['Bearer'])
AUTH_HEADER_PREFIX = f'{_AUTH_TYPES[0]} '


class UserMiddleware(MiddlewareMixin):
    """JWT 鉴权中间件：路径命中关键词才校验，其余放行"""

    def process_request(self, request):
        # 1. 不需要鉴权的路径放行
        if not self._need_auth(request.path_info):
            return None

        # 2. 提取 Authorization 头
        auth_header = (request.META.get(AUTH_HEADER_NAME) or '').strip()
        if not auth_header.startswith(AUTH_HEADER_PREFIX):
            return self._unauthorized_response('未提供有效的 Token')

        token = auth_header[len(AUTH_HEADER_PREFIX):].strip()

        # 3. 解码 + 校验类型
        try:
            payload = decode_token(token, expected_type='access')
        except jwt.ExpiredSignatureError:
            return self._unauthorized_response('Token 已过期')
        except jwt.InvalidTokenError:
            return self._unauthorized_response('Token 无效')

        # 4. 黑名单校验
        if is_blacklisted(payload):
            return self._unauthorized_response('Token 已失效，请重新登录')

        # 5. 挂载用户信息
        user_id = payload.get('user_id')
        if not user_id:
            return self._unauthorized_response('Token 中缺少用户标识')

        request.jwt_user_id = user_id
        request.jwt_phone = payload.get('user_phone')
        request.jwt_payload = payload

        return None

    @staticmethod
    def _need_auth(path):
        """路径含任一关键词 → 需鉴权"""
        return any(kw in path for kw in AUTH_URL_KEYWORDS)

    @staticmethod
    def _unauthorized_response(message):
        """统一 401 响应（与 apis._json_error 三字段格式一致）"""
        return JsonResponse(
            {'status': False, 'message': message, 'content': {}},
            status=401,
        )