"""
maneu/urls.py

路由注册规则：
    - 免登录接口：直接注册，路径任意
    - 需登录接口：路径必须包含 '/auth/'，中间件会自动拦截校验

命名规则：
    - 扫码验证类：xxx_verify
    - 列表类：xxx_list
    - 详情类：xxx_detail
    - 认证类：send_sms / login_by_xxx / refresh_access_token
"""
from django.urls import path

from maneu import views
from maneu import apis

urlpatterns = [
    # ==================== 页面 / 视图 ====================
    path('', views.index, name='index'),
    path('verify_order/', views.verify_order, name='verify_order'),
    path('verify_store/', views.verify_store, name='verify_store'),
    path('verify_report/', views.verify_report, name='verify_report'),

    # ==================== 一、扫码验证类（免登录） ====================
    path('order_verify/', apis.order_verify, name='order_verify'),
    path('store_verify/', apis.store_verify, name='store_verify'),
    path('report_verify/', apis.report_verify, name='report_verify'),

    # ==================== 二、认证类 API（这些是登录/刷新接口，不能带 /auth/） ====================
    path('apis/send_sms/', apis.send_sms, name='send_sms'),
    path('apis/login_by_sms/', apis.login_by_sms, name='login_by_sms'),
    path('apis/login_by_wechat/', apis.login_by_wechat, name='login_by_wechat'),
    path('apis/refresh_access_token/', apis.refresh_access_token, name='refresh_access_token'),

    # ==================== 三、业务 API（需登录，路径含 /auth/） ====================
    # 列表类
    path('apis/auth/order_list/', apis.order_list, name='order_list'),
    path('apis/auth/store_list/', apis.store_list, name='store_list'),
    path('apis/auth/report_list/', apis.report_list, name='report_list'),
    path('apis/auth/repair_list/', apis.repair_list, name='repair_list'),

    # 验证类
    # path('apis/auth/order_verify/', apis.order_verify, name='order_verify'),
    # path('apis/auth/store_verify/', apis.store_verify, name='store_verify'),
    # path('apis/auth/report_verify/', apis.report_verify, name='report_verify'),
    # path('apis/auth/repair_verify/', apis.repair_verify, name='repair_verify'),

    # 详情类
    path('apis/auth/order_detail/', apis.order_detail, name='order_detail'),
    path('apis/auth/store_detail/', apis.store_detail, name='store_detail'),
    path('apis/auth/report_detail/', apis.report_detail, name='report_detail'),
    path('apis/auth/repair_detail/', apis.repair_detail, name='repair_detail'),
    path('apis/auth/guest_detail/', apis.guest_detail, name='guest_detail'),

    path('verify_order/VQwxjTJTH5.txt', apis.VQwxjTJTH5, name='VQwxjTJTH5'),

]
