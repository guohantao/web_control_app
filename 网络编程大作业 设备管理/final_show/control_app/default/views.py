#coding=utf-8
from django.shortcuts import render
from django.db.models import Q
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from default.models import Personlist,Machine,User,Temperature_log,Warning_log,State_log
from django.contrib.auth import  authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import logging
import time
from default.email import send_email
import random,json

# Create your views here.

NowUser ='123'
logger = logging.getLogger('django')




#开发者信息页面
def getdeveloper(request):
    user = request.session['username']
    return render(request,'developer.html',{ 'username': user,})

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
   if request.method == 'GET':
       if 'username' in request.session:
           username = request.session['username']
           user = User.objects.filter(username=username)
           machinelist = Machine.objects.filter(user=user)
           return render(request, 'table.html', locals())
       else:
           return render(request, 'login.html')
   elif request.method == 'POST':
       username = request.session['username']
       user = User.objects.filter(username=username)
       machinelist = Machine.objects.filter(SN=request.POST['machinesn'])
       return render(request, 'table.html', locals())

# ajax动态更新主页详情,获取设备列表
def AjaxTable(request):
    username = request.session['username']
    NowUser=username   #设置全局变量
    user = User.objects.get(username=username)
    print("username:::::"+username)
    print('AJAX：NOUSER：'+NowUser)
    machinel = Machine.objects.filter(user=user)
    machinelist = []
    all_machine = len(machinel)
    run_machine = 0
    stop_machine = 0
    pause_machine = 0
    break_machine = 0
    for item in machinel:
        temp = {'id': item.id, 'SN': item.SN, 'name': item.name, 'temperature': item.temperature, 'time': item.time,
                'warning': item.warning, 'state': item.state, 'limit': item.limit}
        machinelist.append(temp)
        if item.state == "正常":
            run_machine += 1
        elif item.state == "暂停":
            pause_machine += 1
        elif item.state == "关闭":
            stop_machine += 1
        elif item.state == "故障":
            break_machine += 1

    res = {'success': "true", "machinelist": machinelist,'all_machine':all_machine,'run_machine':run_machine,'stop_machine':stop_machine,'pause_machine':pause_machine,'break_machine':break_machine}
    return JsonResponse(res)

def warning_histort(request):
    username = request.session['username']
    user = User.objects.get(username=username)
    machinelist = Machine.objects.filter(user=user)
    warning_list= []
    for item in machinelist:
        warningl = Warning_log.objects.filter(Q(machine=item) , ~Q(history_warning = "无"))
        warning_list.extend(warningl)
    return render(request,'warning_history.html',locals())

def warning_history_ajax(request):
    username = request.session['username']
    user = User.objects.get(username=username)
    machinelist = Machine.objects.filter(user=user)
    warning_list = []
    for item in machinelist:
        warningl = Warning_log.objects.filter(Q(machine=item), ~Q(history_warning="无"))
        warning_list.extend(warningl)
        dictionary_warning_list = []
    for item in warning_list:
        temp = {'id':item.id,'SN':item.machine.SN,'history_warning':item.history_warning,'warning_change_time':item.warning_change_time}
        dictionary_warning_list.append(temp)
    res = {'success':'true','warning_list':dictionary_warning_list}
    return JsonResponse(res)




#----------------------------设备添加修改删除---------------------
# @login_required()
# 添加设备
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
        tempera_log = Temperature_log(machine=machine,history_temperature=tempera,temperature_change_time=Time)
        warning_log = Warning_log(machine=machine,history_warning=warning,warning_change_time=Time)
        state_log = State_log(machine=machine,history_state=state,state_change_time=Time)
        tempera_log.save()
        warning_log.save()
        state_log.save()
        machinelist = Machine.objects.filter(user=user)
        #监测函数，检测温度有没有到阈值
        detection(machine.SN,user)
        return render(request,'table.html',{'machinelist':machinelist,'username':username})
#ajax实现开
def open(request):
    machineid = request.GET['machineid']
    machine = Machine.objects.get(id=machineid)
    if machine.state == "关闭" :
        machine.state = "正常"
        machine.save()
        Time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        statelog = State_log(machine=machine, history_state=machine.state, state_change_time=Time)
        statelog.save()
    res = {'success': "true"}
    print(res)
    return JsonResponse(res)

#ajax实现关
def close(request):
    # 改变状态为关并记录
    machineid = request.GET['machineid']
    machine = Machine.objects.get(id=machineid)
    if machine.state != "关闭":
        machine.state = "关闭"
        machine.save()
        Time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        statelog = State_log(machine=machine, history_state=machine.state, state_change_time=Time)
        statelog.save()
    res = {'success': "true"}
    print(res)
    return JsonResponse(res)

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
            temperature_log = Temperature_log(machine=machine,history_temperature=machine.temperature,temperature_change_time=machine.time)
            temperature_log.save()

        if machine.warning != wr :
            warning_log = Warning_log(machine=machine,history_warning=machine.warning,warning_change_time=machine.time)
            warning_log.save()

        if machine.state != st :
            state_log = State_log(machine=machine,history_state=machine.state,state_change_time=machine.time)
            state_log.save()


        machinelist = Machine.objects.filter(user=user)
        # 监测函数，检测温度有没有到阈值
        detection(machine.SN,user)
        return render(request,'table.html',{'machinelist':machinelist,'username':username})

# @login_required()
def dellist(request):
    machineid= request.GET['machineid']
    Machine.objects.get(id=machineid).delete()
    # Temperature_log.delete(machine= machine)

    res = {"success":"true"}
    return  JsonResponse(res)

# 显示该设备详情,POST方式实现动态刷新
def detail(request):
    if request.method == "GET":
        print("jin ru detail get")
        machineid = request.GET['machineid']
        print("detail id:"+machineid)
        machine = Machine.objects.get(id=machineid)
        username = request.session['username']
        return render(request, 'detail.html', {'machine': machine, 'username': username})
    elif request.method == 'POST':
        print("jin ru detail get")
        username = request.session['username']
        user = User.objects.filter(username=username)
        machinelist = Machine.objects.filter(SN=request.POST['machinesn'],user = user)
        if(len(machinelist)!= 0 ):
            machine=machinelist[0]

        return render(request, 'detail.html', locals())

#ajax实现log表动态刷新
def get_log_table(request):
    machineid = request.POST['machineid']
    print("machineid:"+machineid)
    machine = Machine.objects.get(id=machineid)
    print(machine)
    state_log = []
    temperature_log = []
    warning_log = []
    statelist = State_log.objects.filter(machine=machine)
    temperaturelist = Temperature_log.objects.filter(machine=machine)
    warninglist = Warning_log.objects.filter(machine=machine)
    for item in statelist:
        temp = {'state': item.history_state, 'time': item.state_change_time}
        state_log.append(temp)
    for item in temperaturelist:
        temp = {'temperature': item.history_temperature, 'time': item.temperature_change_time}
        temperature_log.append(temp)
    for item in warninglist:
        temp = {'warning': item.history_warning, 'time': item.warning_change_time}
        warning_log.append(temp)
    res = {'success': "true", 'state_log': state_log, 'temperature_log': temperature_log, 'warning_log': warning_log}
    return JsonResponse(res)

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
                NowUser = username
                print("Loin1111"+NowUser)
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
            return render(request, 'login.html',{"notice":"无此用户，或密码错误，请确认用户名和密码！"})
            #return HttpResponseRedirect("/login/")

            #重定向到失败页面，省略
        print (request.session.keys())
        #print request.session['_auth_user_id']
        return HttpResponseRedirect("/")


def my_logout(request):
    logout(request)
    NowUser = None
    print (request.session.keys())
    return render(request,'login.html',{'notice':"请登录"})


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
        return render(request, 'login.html',{'notice':"该用户已注册,请直接登录"})

    user = User.objects.create_user(username=na,email=em,password=password)
    user.save()
    print("creat a User")
    return render(request,'login.html',{'notice':"注册成功，请登录"})


def user_set(request):
    if request.method == 'GET':
        username = request.session['username']
        user = User.objects.get(username=username)
        return render(request,'user_set.html',{'username':username,'password':user.password})
    elif request.method == 'POST':
        username = request.session['username']
        old_password = request.POST['old_password']
        new_password = request.POST['new_password_affirm']
        user = User.objects.get(username=username)
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            my_logout(request)
            return render(request,'login.html',{'notice':"请登录"})
        else:
            return render(request, 'user_set.html',{'username': username, 'password': user.password, 'result_information': "原始密码输入错误"})


# -------------------------------------------------------状态监测-------------------------------------
def detection(SN,user):
    machine = Machine.objects.get(SN=SN)
    if int(machine.temperature) > int(machine.limit):

        send_email(user.email, machine.SN)

#此处需要一个全局变量来处理当前用户的的问题
#
def client_model(request):
    #print(NowUser)
    if request.method == 'GET':
        if NowUser ==None:
            return JsonResponse({})    #如果出现未登陆状态，则返回空

        machineALL = Machine.objects.all()
        if len(machineALL)==0:
            #print("向客户端发送！(get)")
            return JsonResponse({})
        else:
            sendMachine = {}
            for item in machineALL:
                if item.state ==  "正常":
                    sendMachine[item.SN]=item.limit
            print("向客户端发送：（get）")
            print(sendMachine)  # 检查是否已经构建好字典
            return JsonResponse(sendMachine)

        #之前的版本
        # userN=User.objects.get(username=NowUser)
        # sendMachine={}
        # machineALL = Machine.objects.filter(user=userN)
        # print(machineALL)
        #
        # if len(machineALL)==0:
        #     print("Don't have any equipment!")
        #     return JsonResponse(sendMachine)
        #
        # for item in machineALL:
        #     print (item.SN)
        #     print(item.limit)
        #     sendMachine[item.SN]=item.limit
        #
        # print(sendMachine)    #检查是否已经构建好字典
        # return JsonResponse(sendMachine)

    elif request.method == 'POST':

        allList = request.POST
        print("客户端获得：")
        print(allList)

        for item in allList:
            changeM=Machine.objects.get(SN=item)
            if len(Machine.objects.filter(SN=item))==0:
                print("无此用户！")
                pass
            else:
                Time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                changeM.temperature=allList[item]
                changeM.time=Time
                changeM.warning='无'
                changeM.save()
                detection(item,changeM.user)

                if int(allList[item])>int(changeM.limit):
                        print("超过温度！"+allList[item]+">"+changeM.limit)
                        P=Warning_log(machine=changeM,history_warning="温度超过阈值",warning_change_time=Time)
                        changeM.warning='报警'
                        changeM.save()
                        P.save()
                Temp=Temperature_log(machine=changeM,history_temperature=allList[item],temperature_change_time=Time)
                Temp.save()

        machineALL = Machine.objects.all()
        if len(machineALL) == 0:
            print("返回设备列表为空！(post)")
            return JsonResponse({})
        else:
            sendMachine = {}
            for item in machineALL:
                if item.state == "正常":
                    sendMachine[item.SN] = item.limit
            print("正常返回设备列表！(post)")
            print(sendMachine)  # 检查是否已经构建好字典
            return JsonResponse(sendMachine)

        #之前的版本
        # if NowUser is None:
        #     #print("当前无用户登录！")
        #     return JsonResponse({})  # 如果出现未登陆状态，则返回空
        #
        # userN = User.objects.get(username=NowUser)
        # allList=request.POST
        #
        #
        # for item in allList:
        #     changeM=Machine.objects.get(SN=item)
        #
        #     if len(Machine.objects.filter(SN=item))==0:
        #         print("无此用户！")
        #         pass
        #     else:
        #         print("有此用户！")
        #         if changeM.state=="正常":
        #             print("进入数据库操作！")
        #             Time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        #             changeM.temperature=allList[item]
        #             changeM.time=Time
        #             changeM.warning='无'
        #             changeM.save()
        #             detection(item,userN)
        #
        #             if int(allList[item]>changeM.limit):
        #                 P=Warning_log(machine=changeM,history_warning="温度超过阈值",warning_change_time=Time)
        #                 changeM.warning='报警'
        #                 changeM.save()
        #                 P.save()
        #             Temp=Temperature_log(machine=changeM,history_temperature=allList[item],temperature_change_time=Time)
        #             Temp.save()
        #
        #
        # print("post bunch!")
        # print(request.POST)
        #
        # userN = User.objects.get(username=NowUser)
        # sendMachine = {}
        # machineALL = Machine.objects.filter(user=userN)
        # #print(machineALL)    #返回的设备列表
        #
        # if len(machineALL) == 0:
        #     print("Don't have any equipment!")
        #     return JsonResponse(sendMachine)
        #
        # for item in machineALL:
        #     #print(item.SN)
        #     #print(item.limit)
        #     sendMachine[item.SN] = item.limit
        #
        # # #print(sendMachine)  # 检查是否已经构建好字典
        # return JsonResponse(sendMachine)
#
# #下面的部分为原始的设计
# # def client_model(request):
# #     print("ok get into this view function!")
# #     if NowUser is None:
# #         return render(request,'')
# #     else:
# #         print(NowUser)
# #         machineALL=Machine.objects.filter(user=NowUser)    #返回值为list
# #         for item in machineALL:
# #             if item.state=='关闭':
# #                 pass
# #             else:
# #                 Mlimit=item.limit #阈值
# #                 climateR=random.randint(0,Mlimit+5)
# #                 M=Machine.objects.get(SN=item.SN)
# #                 M.temperature=climateR
# #                 M.save()
# #
# #                 Time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
# #                 tempera_log = Temperature_log(machine=M,history_temperature=climateR,temperature_change_time=Time)
# #                 tempera_log.save()
# #                 detection(item.SN,NowUser)
# #                 if climateR>=Mlimit:
# #                     store_warning_log=Warning_log(machine=M,history_warning='报警')
# #                     store_warning_log.save( )
# #
# #     return render(request,'login.html',{'notice':"请登录"})