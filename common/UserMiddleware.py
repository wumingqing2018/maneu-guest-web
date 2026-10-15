"""
common/UserMiddleware.py

用户登录校验中间件（基于 JWT）

规则（重要）：
  路径里含 JWT_CONFIG['AUTH_URL_KEYWORDS'] 中的任意关键词（默认 '/auth/'）
  → 走 JWT 校验
  否则 → 直接放行

职责：
  1. 判断当前路径是否需要鉴权
  2. 从 Authorization 头提取 access token
  3. 校验类型、签发者、黑名单
  4. 将 user_id / user_phone / payload 挂到 request 上
"""
import jwt
from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from common.util_jwt import decode_token, is_blacklisted

JWT_CONFIG = settings.JWT_CONFIG

# ⭐ 需要鉴权的路径关键词
AUTH_URL_KEYWORDS = JWT_CONFIG.get('AUTH_URL_KEYWORDS', ['/auth/'])

AUTH_HEADER_NAME = JWT_CONFIG.get('AUTH_HEADER_NAME', 'HTTP_AUTHORIZATION')
AUTH_HEADER_PREFIX = JWT_CONFIG['AUTH_HEADER_TYPES'][0] + ' '   # 'Bearer '


class UserMiddleware(MiddlewareMixin):

    def process_request(self, request):
        # 1. 不需要登录的路径，直接放行
        if not self._need_auth(request.path_info):
            return None

        # 2. 取 Authorization 头
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

        # 5. 挂载到 request，供视图直接使用
        user_id = payload.get('user_id')
        if not user_id:
            return self._unauthorized_response('Token 中缺少用户标识')

        request.jwt_user_id = user_id
        request.jwt_phone   = payload.get('user_phone')
        request.jwt_payload = payload

        return None

    @staticmethod
    def _need_auth(path):
        """路径含关键词 → 需要登录"""
        return any(kw in path for kw in AUTH_URL_KEYWORDS)

    @staticmethod
    def _unauthorized_response(message):
        return JsonResponse(
            {'status': False, 'message': message},
            status=401,
        )