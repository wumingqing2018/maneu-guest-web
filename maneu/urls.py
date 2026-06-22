"""maneu URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from maneu import views
from maneu import api


urlpatterns = [
    path('', views.index, name='index'),
    path('verify_order/', views.verify_order, name='verify_order'),
    path('verify_store/', views.verify_store, name='verify_store'),
    path('verify_report/', views.verify_report, name='verify_report'),
    path('sendsms/', api.sendsms, name='sendsms'),
    path('login_wx/', api.login_wx, name='login_wx'),
    path('login_sms/', api.login_sms, name='login_sms'),
    path('get_list/', views.get_list, name='get_list'),
    path('get_index/', views.get_index, name='get_index'),
    path('get_detail/', views.get_detail, name='get_detail'),
    path('order_verify/', api.order_verify, name='order_verify'),
    path('store_verify/', api.store_verify, name='store_verify'),
    path('report_verify/', api.report_verify, name='report_verify'),

]
