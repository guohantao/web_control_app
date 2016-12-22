#coding=utf-8
from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from default.models import Personlist,Machine,User
from django.contrib.auth import  authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import logging

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


# @login_required()
def addlist(request):
    if request.method == 'GET':
        return render(request,'form-elements.html')
    elif request.method == 'POST':
        username = request.session['username']
        user=User.objects.get(username=username)
        sn = request.POST['SN']
        na= request.POST['name']
        tempera = request.POST['temperature']
        # time = request.POST['time']
        state = request.POST['state']
        warning = request.POST['warning']
        machine = Machine
        machine = Machine(user=user,SN=sn,name=na,temperature=tempera,state=state,warning=warning)
        machine.save()
        machinelist = Machine.objects.filter(user=user)
        return render(request,'table.html',{'machinelist':machinelist,'username':username})







def getaddpage(request):
    if 'username' in request.session:
        username = request.session['username']
        return render(request, 'table.html', locals())
    else:
        return render(request, 'login.html')






# def getlist(request):
#    # personlist = Personlist.objects.all()
#     #logger.info("XXXXXXXXXXXXXXXXXXXXXXXXlogging")
#     return render(request, 'index.html')


# @login_required()
def updatelist(request):
    if request.method == 'GET':
        username = request.session['username']
        machine_id = request.GET['machineid']
        machine = Machine.objects.get(id=machine_id)
        return render(request,'form-elements.html',{'machine':machine,'username':username})
    elif request.method == 'POST':
        machine_id = request.POST['id']
        machine = Machine.objects.get(id=machine_id)
        username = request.session['username']
        user = User.objects.get(username=username)
        machinelist = Machine.objects.filter(user=user)
        machine.SN = request.POST['SN']
        machine.name = request.POST['name']
        machine.temperature = request.POST['temperature']
        # machine.time = request.POST['time']
        machine.state = request.POST['state']
        machine.warning = request.POST['warning']
        machine.save()



        return render(request,'table.html',{'machinelist':machinelist,'username':username})

# @login_required()
def dellist(request):
    machineid= request.GET['machineid']
    print(machineid)
    Machine.objects.get(id=machineid).delete()
    username=request.session['username']
    user = User.objects.get(username=username)
    machinel = Machine.objects.filter(user=user)
    machinelist=[]
    for item in machinel:
        temp = {'id':item.id,'SN':item.SN,'name':item.name,'temperature':item.temperature,'warning':item.warning,'state':item.state}
        machinelist.append(temp)

    res={'success':"true","machinelist":machinelist}
    print(res)
    return  JsonResponse(res)

def detail(request):
    machineid = request.GET['machineid']
    machine = Machine.objects.get(id=machineid)
    username = request.session['username']
    return  render(request,'detail.html',{'machine':machine,'username':username})












def searchlist(request):
    if request.method == 'GET':
        return render(request,'search.html')
    elif request.method == 'POST':
        na = request.POST['name']
        per = Personlist.objects.filter(name=na)
        return render(request,'showsearch.html',locals())









    return  render(request,'table.html',{'personlist':personlist})


def my_login(request):
    if request.method == 'GET':
        return render(request,'login.html')
    elif request.method == 'POST':
        username= request.POST['username']
        password= request.POST['password']
        user = authenticate(username=username,password=password)
        if user is not None:
            if user.is_active:
                request.session['username']=username
                login(request,user)
                print(username)
                return HttpResponseRedirect("/")
                #重定向到成功页面
            else:
                print ("user is not active")
                #重定向到失败页面，省略
        else:
            print ("user is None")

            return HttpResponseRedirect("/login/")
            #重定向到失败页面，省略
        print (request.session.keys())
        #print request.session['_auth_user_id']
        return HttpResponseRedirect("/")


def my_logout(request):
    logout(request)
    print (request.session.keys())
    return HttpResponseRedirect("/")

def register(request):

    na = request.POST['username']
    em = request.POST['email']
    password = request.POST['password']
    user = User.objects.create_user(username=na,email=em,password=password)
    user.save()
    print("creat a User")
    return render(request,'login.html')

