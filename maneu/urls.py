"""
maneu/urls.py
你可以这个注释段落添加注释，方便下次检查优化及记录

路由注册规则（重要）：
  - 免登录接口：直接注册，路径任意
  - 需登录接口：路径必须包含 '/auth/'，中间件会自动拦截校验

分组说明：
  1. 页面 / 视图
  2. 扫码验证类（免登录）
  3. 认证类 API（免登录：发送验证码、登录、刷新）
  4. 静态资源类 API（免登录）
  5. 业务 API（需登录，路径含 /auth/，后期开放）
"""
from django.urls import path

from maneu import views
from maneu import apis

urlpatterns = [
    # ==================== 1. 页面 / 视图 ====================
    path('', views.index, name='index'),

    # ==================== 2. 扫码验证类（免登录） ====================
    path('verify_order/',   views.verify_order,   name='verify_order'),
    path('verify_store/',   views.verify_store,   name='verify_store'),
    path('verify_report/',  views.verify_report,  name='verify_report'),

    path('order_verify/',   apis.order_verify,     name='order_verify'),
    path('store_verify/',   apis.store_verify,     name='store_verify'),
    path('report_verify/',  apis.report_verify,    name='report_verify'),

    # ==================== 3. 认证类 apis（免登录） ====================
    path('apis/sendsms/',              apis.sendsms,              name='sendsms'),
    path('apis/access_token_sms/',     apis.access_token_sms,     name='access_token_sms'),
    path('apis/access_token_weixin/',  apis.access_token_weixin,  name='access_token_weixin'),
    path('apis/refresh_token/',        apis.refresh_token,        name='refresh_token'),

    # ==================== 4. 业务 apis（需登录，路径含 /auth/） ====================
    # ⚠️ 以下接口当前暂不开放，等前端准备好后取消注释即可自动走 JWT 校验
    #
    path('apis/auth/order_list/',    apis.order_list,    name='order_list'),
    path('apis/auth/report_list/',   apis.report_list,   name='report_list'),
    path('apis/auth/store_list/',    apis.store_list,    name='store_list'),
    path('apis/auth/repair_list/',   apis.repair_list,   name='repair_list'),

    path('apis/auth/order_detail/',  apis.order_detail,  name='order_detail'),
    path('apis/auth/store_detail/',  apis.store_detail,  name='store_detail'),
    path('apis/auth/report_detail/', apis.report_detail, name='report_detail'),
    path('apis/auth/repair_detail/', apis.repair_detail, name='repair_detail'),

    path('apis/auth/guest_detail/',  apis.guest_detail,  name='guest_detail'),
]