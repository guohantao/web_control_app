import smtplib
from email.mime.text import MIMEText
from email.header import Header
from control_app import settings
from email.mime.text import MIMEText
sender = '17888821952@163.com'
receivers = ['850165905@qq.com']
content="你二大爷家的电饭锅炸了！"


def send_email(Nmail,equ):

    me="equipment management"+'<'+settings.EMAIL_HOST_USER+">"   #此处只能为英文
    msg=MIMEText(content,_subtype="plain")

    msg["Subject"]="设备"+equ+"故障报警"
    msg["From"]=me
    msg['To']=";".join([Nmail])

    sever=smtplib.SMTP()
    try:
        sever.connect(settings.EMAIL_HOST)
    except:
        print("connect fail!")
        return

    try:
        sever.login(settings.EMAIL_HOST_USER,settings.EMAIL_HOST_PASSWORD)
    except:
        print ("login fail!")
        return
    try:
        sever.sendmail(me,[Nmail],msg.as_string())
        sever.close()
    except Exception as e:
        print("send fail!")
        print (e)
        return

    print ("邮件发送成功！")
    return
