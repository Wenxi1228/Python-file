# 导入socket模块
import socket
import time
import datetime
import threading
# 创建socket对象
def socket_tcp(ip_addr,send_port):
    s = socket.socket()
    # 连接远程主机
    s.connect((ip_addr, send_port))
    #print('--%s--' % s.recv(1024).decode('utf-8'))
    print(datetime.datetime.now())
    time.sleep(5)
    s.close()
    time.sleep(5)


if __name__=='__main__':
    while 1:
        socket_tcp('172.31.3.67',30517)