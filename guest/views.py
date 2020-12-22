# django shortcuts 组件
from django.shortcuts import render
from django.shortcuts import HttpResponse

# service 层
from .service import find_order
from my_lib import verify_lib


# Create your views here.


def index(request):
    """
    授权产品页面
    """
    return render(request, "guest/index.html")


def check_order(request, order_id, token):
    """
    查找订单
    """
    verify1 = verify_lib.order_id(order_id)
    verify2 = verify_lib.token(token)
    if verify1 and verify2:
        order = find_order(order_id, token)
        if order:
            return render(request, 'guest/check_order.html', {'order': order})
    else:
        return HttpResponse('啥都没有找到')
