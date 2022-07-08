import time
from contextlib import suppress
import paramiko

# 创建一个ssh的客户端，用来连接服务器
def read_timestamp(host_name, device):
    ssh = paramiko.SSHClient()
    # 创建一个ssh的白名单
    know_host = paramiko.AutoAddPolicy()
    #加载创建的白名单
    ssh.set_missing_host_key_policy(know_host)

    # 连接服务器
    with suppress(paramiko.ssh_exception.AuthenticationException):
       ssh.connect(hostname=host_name, port=22, username="root", password="")
    ssh.get_transport().auth_none("root")
    # 执行命令
    stdin, stdout, stderr = ssh.exec_command("date")
    # stdin  标准格式的输入，是一个写权限的文件对象
    # stdout 标准格式的输出，是一个读权限的文件对象
    # stderr 标准格式的错误，是一个写权限的文件对象

    tmp = stdout.read().decode().strip('\n')
    print(device,"timestamp is :", tmp)
    ssh.close()
    return tmp

if __name__=='__main__':
    check_times = 1
    result = []
    while check_times <= 500:
        print("The", check_times, "timesync test")
        times="The " + str(check_times) + " timesync test"
        result.append(times)
        J3A_result = read_timestamp("192.168.2.10", "J3A")
        result.append(J3A_result)
        J3B_result = read_timestamp("192.168.2.11", "J3B")
        result.append(J3B_result)
        J3C_result = read_timestamp("192.168.2.28", "J3C")
        result.append(J3C_result)
        time.sleep(68.6)
        check_times += 1
    #print(result)
    f = open("D:\J3testlog\Testresult.txt", mode = "w")
    for i in result:
        f.write(i)
        f.write('\r\n')
    f.close()

    

