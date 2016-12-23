#coding=utf-8
from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from default.models import Personlist,Machine,User,Temperature_log,Warning_log,State_log
from django.contrib.auth import  authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import logging
import time


# Create your views here.

logger = logging.getLogger('django')

#获取主页函数

def getindex(request):
    logger.info("XXXXXXXXXXXXXXXXXXXXXXXXlogging")
    if 'username'in request.session:
        username=request.session['username']
        user = User.objects.get(username=username)
        machinelist = Machine.objects.filter(user=user)
        all_machine = 0
        run_machine = 0
        stop_machine = 0
        pause_machine = 0
        break_machine = 0
        for i in range(len(machinelist)):
            all_machine+=1
            if machinelist[i].state == "正常":
                run_machine+=1
            elif machinelist[i].state == "暂停":
                pause_machine+=1
            elif machinelist[i].state == "关闭":
                stop_machine+=1
            elif machinelist[i].state == "故障":
                break_machine+=1

        return render(request,'index.html',locals())
    else:
        return  render(request,'login.html')


@login_required()
def gettable(request):
    if 'username'in request.session:
        username=request.session['username']
        user = User.objects.filter(username=username)
        machinelist = Machine.objects.filter(user=user)
        return render(request,'table.html',locals())
    else:
        return render(request,'login.html')



#----------------------------设备添加修改删除---------------------
# @login_required()
# 已改
def addlist(request):
    if request.method == 'GET':
        return render(request,'form-elements.html')
    elif request.method == 'POST':
        username = request.session['username']
        user=User.objects.get(username=username)
        li =request.POST['limit']
        sn = request.POST['SN']
        na= request.POST['name']
        tempera = request.POST['temperature']
        #获取系统当前时间
        Time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        state = request.POST['state']
        warning = request.POST['warning']
        machine = Machine(user=user, SN=sn, name=na, temperature=tempera, time=Time, state=state, warning=warning,limit=li)
        #检查是否有重名SN
        item = Machine.objects.filter(SN=sn)
        if len(item) != 0:
            return render(request, 'form-elements.html', {'machine': machine, 'username': username,'result_information':"已存在该SN!!"})

        machine.save()
        #创建该机器的LOG日志 !!!!!要先machine.save才能 创建log 要不然数据库会报错，因为machine没有储存进去
        tempera_log = Temperature_log(machine=machine,history_temperature=tempera,history_state=state,history_warning=warning,temperature_change_time=Time,warning_change_time=Time,state_change_time=Time)
        warning_log = Warning_log(machine=machine,history_warning=warning,warning_change_time=Time)
        state_log = State_log(machine=machine,history_state=state,state_change_time=Time)
        tempera_log.save()
        warning_log.save()
        state_log.save()
        machinelist = Machine.objects.filter(user=user)
        return render(request,'table.html',{'machinelist':machinelist,'username':username})

def openclose(request):
    machineid = request.GET['machineid']
    Machine.objects.get(id=machineid).state = "关闭"
    username = request.session['username']
    user = User.objects.get(username=username)
    machinel = Machine.objects.filter(user=user)
    machinelist = []
    for item in machinel:
        temp = {'id': item.id, 'SN': item.SN, 'name': item.name, 'temperature': item.temperature, 'time': item.time,
                'warning': item.warning, 'state': item.state, 'limit': item.limit}
        machinelist.append(temp)

    res = {'success': "true", "machinelist": machinelist}
    print(res)
    return JsonResponse(res)



# #无用
# def getaddpage(request):
#     if 'username' in request.session:
#         username = request.session['username']
#         return render(request, 'table.html', locals())
#     else:
#         return render(request, 'login.html')

# def getlist(request):
#    # personlist = Personlist.objects.all()
#     #logger.info("XXXXXXXXXXXXXXXXXXXXXXXXlogging")
#     return render(request, 'index.html')


# @login_required()
#更新机器表 已改
def updatelist(request):
    if request.method == 'GET':
        username = request.session['username']
        machine_id = request.GET['machineid']
        machine = Machine.objects.get(id=machine_id)
        return render(request,'update.html',{'machine':machine,'username':username})
    elif request.method == 'POST':
        machine_id = request.POST['id']
        machine = Machine.objects.get(id=machine_id)
        username = request.session['username']
        user = User.objects.get(username=username)


        machine.SN = request.POST['SN']
        machine.name = request.POST['name']
        machine.time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        machine.limit = request.POST['limit']
        #保存原来的值，作为比对是否更改
        te = machine.temperature
        st = machine.state
        wr = machine.warning
        machine.state = request.POST['state']
        machine.warning = request.POST['warning']
        machine.temperature = request.POST['temperature']
        machine.save()

        if machine.temperature != te :
            temperature_log = Temperature_log(machine=machine,history_temperature=te,temperature_change_time=machine.time)
            temperature_log.save()

        if machine.warning != wr :
            warning_log = Warning_log(machine=machine,history_warning=wr,warning_change_time=machine.time)
            warning_log.save()

        if machine.state != st :
            state_log = State_log(machine=machine,history_state=st,state_change_time=machine.time)
            state_log.save()


        machinelist = Machine.objects.filter(user=user)
        return render(request,'table.html',{'machinelist':machinelist,'username':username})




# @login_required()
def dellist(request):
    machineid= request.GET['machineid']
    print(machineid)
    print(Machine.objects.get(id=machineid).name)
    Machine.objects.get(id=machineid).delete()
    username=request.session['username']
    user = User.objects.get(username=username)
    machinel = Machine.objects.filter(user=user)
    machinelist=[]
    for item in machinel:
        temp = {'id':item.id,'SN':item.SN,'name':item.name,'temperature':item.temperature,'time':item.time , 'warning':item.warning,'state':item.state,'limit':item.limit}
        machinelist.append(temp)

    res={'success':"true","machinelist":machinelist}
    print(res)
    return  JsonResponse(res)

# 显示该设备详情
def detail(request):
    machineid = request.GET['machineid']
    machine = Machine.objects.get(id=machineid)
    username = request.session['username']
    return  render(request,'detail.html',{'machine':machine,'username':username})


# #无用
# def searchlist(request):
#     if request.method == 'GET':
#         return render(request,'search.html')
#     elif request.method == 'POST':
#         na = request.POST['name']
#         per = Personlist.objects.filter(name=na)
#         return render(request,'showsearch.html',locals())
#     return  render(request,'table.html',locals())
#
#-------------------------------------用户注册登录管理--------------------------------
def my_login(request):
    if request.method == 'GET':
        return render(request,'login.html',{"notice":" "})

    elif request.method == 'POST':
        username= request.POST['username']
        password= request.POST['password']
        user = authenticate(username=username,password=password)
        if user is not None:
            if user.is_active:
                request.session['username']=username
                login(request,user)
                print("login:"+username)
                return HttpResponseRedirect("/")
                #重定向到成功页面
            else:
                print ("user is not active")
                return render(request, 'login.html', {"notice": "密码错误！"})
                #重定向到失败页面，省略
        else:
            print ("user is None")
            return render(request, 'login.html',{"notice":"无此用户！"})
            #return HttpResponseRedirect("/login/")

            #重定向到失败页面，省略
        print (request.session.keys())
        #print request.session['_auth_user_id']
        return HttpResponseRedirect("/")


def my_logout(request):
    logout(request)
    print (request.session.keys())
    return HttpResponseRedirect("/")


def register(request):
    print("jin ru request")
    na = request.POST['username']
    em = request.POST['email']
    password = request.POST['password']
    # password2=request.POST['password2']
    # if password!=password2:
    #
    users=User.objects.filter(username=na)

    if len(users) != 0:
        print("该用户已注册")
        return render(request, 'register.html')

    user = User.objects.create_user(username=na,email=em,password=password)
    user.save()
    print("creat a User")
    return render(request,'login.html')


