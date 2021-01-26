from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from django.shortcuts import render
from common.common import current_time


class FrequentRequestMiddleware(MiddlewareMixin):
    """
    频繁请求中间件类
    每秒只能请求1次
    """

    def __init__(self, get_response):
        self.get_response = get_response
        print("--频繁请求中间件类启动--")

    def process_request(self, request):
        time = current_time()
        request.session['request_time'] = time
        print(request.session['request_time'])
