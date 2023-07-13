import socket

# 定义SomeIP服务的IP地址和端口
service_ip = '172.16.10.12'
service_port = 30490
source_port = 30490

# 创建UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', source_port))
# 构建订阅请求参数
# someip header
service_id = '0xffff'  #2 bytes
method_id = '0x8100'   #2 bytes
length = '0x00000030'         #4 bytes,长度48
client_id = '0x0001'   #2 bytes
session_id = '0x0001'  #2 bytes
someip_version = '0x01'   #1 byte
interface_version = '0x01'  # 接口版本,1 byte
message_type = '0x02'  #Notification, 1 byte
return_code = '0x00'   #OK, 1 byte
# someip sd
flags = '0xe0000000'   # 4 byte, include 3 byte reserved
length_sd = '0x00000010'      # 4 byte， 长度16
# entry array
Type = '0x06'          # 1 byte
index_1 = '0x00'          # 1 byte
index_2 = '0x00'          # 1 byte
numbers_opts = '0x10'     # 1 byte
service_id_2 = '0x0100'   # 2 byte
instance_id_2 = '0x0001'   # 2 byte
major_version = '0x01'   # 1 byte
ttl = '0x000003'          # 3 byte
reserved_2 = '0x0000'     # 2 byte
event_group_id = '0x0002'  # 2 byte
length_array = '0x0000000C'        # 4 byte
# options array
length_options_array = '0x0009'  # 2 bytes
array_type = '0x0400'
IP = '0xAC100A3C'  #172.16.10.60
reserved_3 = '0x00'
Protocol = '0x11' #UDP
Port_client = '0xbfcc' # 49100
#print(type(hex(Port_client)))

# 构建订阅请求消息
subscription_request = (service_id[2:] + method_id[2:] +length[2:] + client_id[2:] + session_id[2:] + someip_version[2:] + interface_version[2:] + message_type[2:] + return_code[2:]
                        + flags[2:] + length_sd[2:] + Type[2:] + index_1[2:] + index_2[2:] + numbers_opts[2:] + service_id_2[2:] + instance_id_2[2:] + major_version[2:] +ttl[2:]
                        + reserved_2[2:] + event_group_id[2:] + length_array[2:] + length_options_array[2:] + array_type[2:] + IP[2:] + reserved_3[2:] + Protocol[2:] + Port_client[2:])
data = bytes.fromhex(subscription_request)
print(len(data))
print(data)

# 发送订阅请求
sock.sendto(data, (service_ip, service_port))

# 循环接收SomeIP服务的通知消息
while True:
    data, addr = sock.recvfrom(1024)
    print('Received message from:', addr)
    print('Message data:', data)