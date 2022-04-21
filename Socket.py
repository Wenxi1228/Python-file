# 导入socket模块
import socket
import time
import datetime
# 创建socket对象
while 1:
    s = socket.socket()
    # 连接远程主机
    s.connect(('172.31.3.67', 30517))
    #print('--%s--' % s.recv(1024).decode('utf-8'))
    print(datetime.datetime.now())
    time.sleep(5)
    s.close()
    time.sleep(5)