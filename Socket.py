# 导入socket模块
import socket
import time
import datetime
from threading import Thread


# 创建socket对象
def socket_tcp(ip_addr,send_port):
    s = socket.socket()
    server_address = (ip_addr, send_port)
    msg= b'\x10\x10\x00\x01\x00\x00\x00\x4c\x02\x12\x00\x01\x01\x01\x00\x00\x00\x00\x00\x40\x00\x08\x02\x80\x5e\x1f\x01\x02\xac\x1f\x04\x02\x00\x50\x00\x00\x00\x00\x14\x1b\x55\x78\x01\x00\x00\x00\x00\x00\x23\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
    # 连接远程主机
    s.connect((ip_addr, send_port))
    s.sendto(msg, server_address)
    #print('--%s--' % s.recv(1024).decode('utf-8'))
    print(datetime.datetime.now())
    time.sleep(5)
    s.close()
    time.sleep(5)

def socket_udp(ip_addr, send_port):

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    start = time.time()  # 获取当前时间
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start)))  # 以指定格式显示当前时间
    msg= b'\xb0\x08\x00\x01\x00\x00\x00\x4c\x02\x12\x00\x01\x01\x01\x00\x00\x00'
    server_address = (ip_addr, send_port)  # 接收方 服务器的ip地址和端口号
    client_socket.sendto(msg, server_address)  # 将msg内容发送给指定接收方
    now = time.time()  # 获取当前时间
    run_time = now - start  # 计算时间差，即运行时间
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now)))
    print("run_time: %d seconds\n" % run_time)
    time.sleep(1)


if __name__=='__main__':
    #t1=Thread(target=socket_tcp('172.31.3.67', 30517))
    #t2=Thread(target=socket_udp('172.31.3.67', 41509))
    #t1.start()
    #t2.start()

    while 1:
        socket_tcp('172.31.3.67', 30517)
        socket_udp('172.31.3.67', 41509)