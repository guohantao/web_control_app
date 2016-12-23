#coding=utf-8
from django.conf.urls import url

from . import views

urlpatterns = [

     url(r'^$',views.getindex),  #主页面
     url(r'^table/$',views.gettable),  #设备管理页面
     url(r'^register/$',views.register),#注册账号
     url(r'^add/$',views.addlist),#添加设备
     url(r'^update/$',views.updatelist),#更新设备信息
     url(r'^del/$',views.dellist),#删除设备
     url(r'^detail/$',views.detail),#设备详细
     url(r'^openclose/$',views.openclose),#设备详细
     url(r'^addpage/$',views.getaddpage),  #打开查找页面

     # 以下函数未定义，你们自己在VIEW里写
     url(r'^warning_history/$',views.getindex),  #报警历史
     url(r'^set/$',views.getindex),  #打开设置页面



     url(r'^login/$',views.my_login), #登陆
     url(r'^logout/$',views.my_logout),#注销

]