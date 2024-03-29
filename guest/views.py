from django.shortcuts import render
from django.shortcuts import HttpResponse

# service 层
from .service import find_order
from common import verify_lib


def index(request):
    """
    授权产品页面
    """
    return render(request, "guest/index.html")


def order(request, order_id, token):
    """
    查找订单
    """
    order = find_order(order_id, token)
    if order:
        return render(request, 'guest/order.html', {'order': order})
    else:
        return HttpResponse('啥都没有找到1')
