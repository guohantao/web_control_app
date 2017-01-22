import threading,time,random
import urllib.request
import urllib.parse
import json
pointURL='http://127.0.0.1:8000/client_model/'
def client_model():
    NowMachine = urllib.request.urlopen(pointURL)
    NowM=NowMachine.read().decode()
    NowM=json.loads(NowM)   #由json转换为dict
    while True:
        send_climate={}    #定义一个字典
        Wtime = 4
        # Wtime = random.randint(0, 4)
        print("Wait time:%d" % Wtime)
        time.sleep(Wtime)

        if len(NowM) == 0:
            print("获取设备列表为空，返回为空！")
        else:
            print("进入！")
            for item in NowM:
                Mlimit=NowM[item]
                print(Mlimit)
                randomC=random.randint(0,int(Mlimit)+5)
                send_climate[item]=str(randomC)

                #以上用于模拟好温度
            print("返回设备模拟列表！")


        data = urllib.parse.urlencode(send_climate)
        data = data.encode('utf-8')
        print(data)
        req = urllib.request.Request(pointURL, data)
        NowMachine = urllib.request.urlopen(req)
        NowM = NowMachine.read().decode()
        NowM = json.loads(NowM)  # 由json转换为dict
            #print (NowM)
            # test_data_urlencode = urllib.urlencode(send_climate)    #采用post的方式返回温度值
            # req = urllib.request.Request(url=pointURL, data=test_data_urlencode)
            # #此处需要进行返回字典的对比，如果一致，则忽略，否则更改NowMachine

    return

client_model()