# 导入socket模块
import socket
import time
import datetime
from threading import Thread


# 创建socket对象
def socket_tcp(ip_addr,send_port):
    s = socket.socket()  #create tcp socket
    server_address = (ip_addr, send_port)
    msg= b'\x10\x10\x00\x01\x00\x00\x00\x4c\x02\x12\x00\x01\x01\x01\x00\x00\x00\x00\x00\x40\x00\x08\x02\x80\x5e\x1f\x01\x02\xac\x1f\x03\x02\x00\x50\x00\x00\x00\x00\x14\x1b\x55\x78\x01\x00\x00\x00\x00\x00\x23\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
    # 连接远程主机
    s.connect((ip_addr, send_port))
    #s.sendto(msg, server_address)
    #print('--%s--' % s.recv(1024).decode('utf-8'))
    print(datetime.datetime.now())
    time.sleep(5)
    #s.close()
    time.sleep(200)

def http_socket():
    # 实例化socket对象  声明：IP4协议          TCP协议
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 绑定   地址          端口
    s.bind(('192.168.2.28', 80))
    # 监听  允许接入客户端数量  一般设置 5
    s.listen(5)
    # 接收客户端连接和客户端地址
    conn, addr = s.accept()
    # 接收数据
    a = conn.recv(1024)  # 1024为客户端发送数据大小上限
    print(a.decode('utf8'))  # 打印接收的数据

if __name__=='__main__':
    #t1=Thread(target=socket_tcp('172.31.3.67', 30517))
    #t2=Thread(target= http_socket())
    #t2.start()
    #t1.start()

    #while 1:

    socket_tcp('172.31.3.67',30517)
    #socket_tcp('192.168.2.28', 80)
    #http_socket()
