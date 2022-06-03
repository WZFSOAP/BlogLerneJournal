import random
import smtplib
import getpass
from email.mime.text import MIMEText
from email.header import Header


def try_send(receiver):
    code = str(random.randint(1000,10000))
    sender = '1197382542@qq.com'
    message = MIMEText("[GOO] Your verification code is: " + code, 'plain', 'utf-8')
    message['From'] = Header("GOO BLOG", 'utf-8')
    message['To'] = Header("Learner", 'utf-8')
    subject = 'Please input the code in your register box.'
    message['Subject'] = Header(subject, 'utf-8')
    server = smtplib.SMTP("smtp.qq.com", 25)
    server.ehlo()
    password = 'ifqmyxyxswbxhaib'
    server.login("1197382542@qq.com", password)
    server.sendmail("1197382542@qq.com", receiver, message.as_string())
    server.quit()
    return code;


