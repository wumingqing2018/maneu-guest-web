import time

from common import common
from django.utils.deprecation import MiddlewareMixin


class FrequentRequestMiddleware(MiddlewareMixin):
    """
    频繁请求中间件类
    每秒只能请求1次
    如果同一个session 每秒请求超过一次就会延迟10秒
    """

    def __init__(self, get_response):
        self.get_response = get_response
        print("--频繁请求中间件类启动--")

    def process_request(self, request):
        current_time = common.current_time()
        try:
            request_time = request.session['request_time']
        except:
            request.session['request_time'] = current_time
            request_time = current_time
        if current_time == request_time:
            time.sleep(10)
            print('频繁请求')
        else:
            request.session['request_time'] = current_time
            print('正常请求')
