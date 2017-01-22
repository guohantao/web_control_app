#coding=utf-8
from django.conf.urls import url

from . import views

urlpatterns = [

     url(r'^$',views.getindex),  #主页面
     url(r'^developer/$', views.getdeveloper),  # 主页面
     url(r'^table/$',views.gettable),  #设备管理页面
     url(r'^register/$',views.register),#注册账号
     url(r'^add/$',views.addlist),#添加设备
     url(r'^update/$',views.updatelist),#更新设备信息
     url(r'^del/$',views.dellist),#删除设备
     url(r'^detail/$',views.detail),#设备详细
     url(r'^open/$',views.open),#开设备
     url(r'^close/$',views.close),#关设备
     url(r'^logtable/$',views.get_log_table),#ajax设备log_table
     url(r'^AjaxTable/$',views.AjaxTable),#ajax所有设备表
     url(r'^user_set/$',views.user_set),#ajax用户更改密码
     url(r'^search_machine/$',views.detail),  #打开查找页面
     url(r'^warning_history/$',views.warning_histort),  #报警历史
     url(r'^ajax_warning/$',views.warning_history_ajax),  #报警历史
     url(r'client_model/$',views.client_model),


     url(r'^login/$',views.my_login), #登陆
     url(r'^logout/$',views.my_logout),#注销

]