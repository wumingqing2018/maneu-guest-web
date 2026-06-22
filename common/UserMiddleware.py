import jwt
from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin


class UserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if 'api' not in request.path.lower():
            return None

        auth_header = request.headers.get('Authorization', '').strip()  # 关键修改
        if not auth_header.startswith('Bearer '):
            return self._unauthorized_response('未提供有效的 Token')

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(
                token,
                settings.JWT_CONFIG['SECRET_KEY'],
                algorithms=[settings.JWT_CONFIG['ALGORITHM']]
            )
            user_id = payload.get('user_id')
            if not user_id:
                return self._unauthorized_response('Token 中缺少用户标识')
            request.jwt_user_id = user_id
        except jwt.ExpiredSignatureError:
            return self._unauthorized_response('Token 已过期')
        except jwt.InvalidTokenError:
            return self._unauthorized_response('Token 无效')

        return None

    def _unauthorized_response(self, message):
        return JsonResponse(
            {'status': False, 'message': message},
            status=401
        )