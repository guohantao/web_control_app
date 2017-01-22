from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Personlist(models.Model):
    name = models.CharField(max_length=10)
    tel = models.CharField(max_length=10)
    email = models.CharField(max_length=10)
    address = models.CharField(max_length=10)
    QQ = models.CharField(max_length=10)

#用户
# class User(models.Model):
#     Username = models.CharField(max_length=10)
#     email = models.EmailField(max_length=20)
#     password = models.CharField(max_length=10)

#设备数据库
class Machine(models.Model):
    user = models.ForeignKey(User)
    SN = models.CharField(max_length=10,unique='true')
    name = models.CharField(max_length=10)
    temperature = models.CharField(max_length=10)
    time = models.CharField(max_length=20)
    warning = models.CharField(max_length=10)
    state = models.CharField(max_length=10)
    limit = models.CharField(max_length=10) #阈值


#每个设备的temperature_log库
class Temperature_log(models.Model):
    machine = models.ForeignKey(Machine)
    history_temperature = models.CharField(max_length=10) #温度
    temperature_change_time = models.CharField(max_length=20) #温度改变时间



#每个设备的state_log库
class State_log(models.Model):
    machine = models.ForeignKey(Machine)
    history_state = models.CharField(max_length=10)  # 状态记录
    state_change_time = models.CharField(max_length=20)  # 状态变化记录生成时间

#每个设备的warning_log库
class Warning_log(models.Model):
    machine = models.ForeignKey(Machine)
    history_warning = models.CharField(max_length=10)  # 报警
    warning_change_time = models.CharField(max_length=20)  # 报警时间