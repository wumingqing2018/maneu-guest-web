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

urlpatterns = [
    path('', views.index, name='index'),
    path('login/',views.login, name='login'),
    path('getOrderList/', views.getOrderList, name='getOrderList'),
    path('getReportList/', views.getReportList, name='getReportList'),
    path('getServiceList/', views.getServiceList, name='getServiceList'),
    path('getOrderDetail/', views.getOrderDetail, name='getOrderDetail'),
    path('getReportDetail/', views.getReportDetail, name='getReportDetail'),
    path('getServiceDetail/', views.getServiceDetail, name='getServiceDetail'),
    path('Test/', views.Test, name='Test'),

]
