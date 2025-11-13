from uuid import uuid4

from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

from common.verify import is_uuid
from maneu.models import ManeuAdmin


class UserMiddleware(MiddlewareMixin):

    def __init__(self, get_response):
        self.get_response = get_response
        print("--用户登录校验中间件启动--")

    def process_request(self, request):
        """
        产生request对象之后---url匹配之前调用
        判断用户是否登录
        白名单内app, 不需要登录
        用户没有登录, 跳转到登录页
        用户已经登录, 允许通过
        """
        request_url = request.path  # method:string, demo:/login/,
        #   判断是否需要校验字段
        print('url', request_url)
        if request_url in ['get_detail', 'get_list', 'get_verify']:
            mark = is_uuid(request.COOKIES.get('mark'))
            if mark:
                admin = ManeuAdmin.objects.filter(password=mark).first()
                if admin:
                    admin.password = str(uuid4())
                    admin.save()
                    request.session['id'] = admin.id
                    request.session['mark'] = admin.password
                    return None
                else:
                    return redirect('login')
            else:
                return redirect('login')
        else:
            return None


    def process_response(self, request, response):
        if request.path in ['get_detail', 'get_list', 'get_verify']:
            response.set_cookie(
                'mark',  # cookie 名称
                request.session.get('mark'),  # cookie 值
                max_age=3600,  # 过期时间（秒）
                path='/',  # 生效路径
                secure=True,  # 仅通过 HTTPS 传输
                httponly=True,  # 防止 JavaScript 访问
                samesite='Lax'  # 防止 CSRF 攻击
            )

            return response
        else:
            response.set_cookie(
                key='mark',  # cookie 名称
                value='',  # cookie 值
                max_age=3600,  # 过期时间（秒）
                path='/',  # 生效路径
                secure=True,  # 仅通过 HTTPS 传输
                httponly=True,  # 防止 JavaScript 访问
                samesite='Lax'  # 防止 CSRF 攻击
            )
            return response
