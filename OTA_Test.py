import time
from contextlib import suppress
import paramiko

# 创建一个ssh的客户端，用来连接服务器
def ota_exe(host_name, device):
    if device =="J3A":
        proc_kill(host_name,device, "ps |grep watchdog_otaser")
    elif device =="J3B":
        proc_kill(host_name, device, "ps |grep watchdog_otaser")
    else:
        proc_kill(host_name, device, "ps |grep watchdog_otaser")
        proc_kill(host_name, device, "ps | grep agent-watchdog")
        proc_kill(host_name, device, "ps | grep agent_module")

def ota_cmd():
    ssh = paramiko.SSHClient()
    # 创建一个ssh的白名单
    know_host = paramiko.AutoAddPolicy()
    # 加载创建的白名单
    ssh.set_missing_host_key_policy(know_host)
    with suppress(paramiko.ssh_exception.AuthenticationException):
        ssh.connect(hostname="192.168.2.28", port=22, username="root", password="")
    ssh.get_transport().auth_none("root")
        #input update cmd
    chan=ssh.invoke_shell()
    print("1")
    chan.send("mount -o rw,remount / \n")
    print("2")
    chan.send("cd /usr/ota/agent_module/ \n")
    print("3")
    chan.send("cp /map/agent_module ./agent_module1 \n")
    print("4")
    chan.send("chmod 777 ./agent_module1 \n")
    print("5")
    chan.send("mount -o ro,remount / \n")
    #print(chan.recv(99999).decode())
    print("6")
    chan.send("./agent_module1 ./config/ 4 > /map/agent.log 2>&1 & \n")
    i=0
    #f = open("D:\\ota\ota.txt", mode="w")
    while i < 100:   #开始升级后等待300s
        #print(chan.recv(99999).decode())
        #f.write(chan.recv(99999).decode())
        time.sleep(3)
        print(i)
        i += 1
    #f.close()
    ssh.close()





def proc_kill(host_name,device,cmdstr):
    ssh = paramiko.SSHClient()
    # 创建一个ssh的白名单
    know_host = paramiko.AutoAddPolicy()
    # 加载创建的白名单
    ssh.set_missing_host_key_policy(know_host)
    with suppress(paramiko.ssh_exception.AuthenticationException):
        ssh.connect(hostname=host_name, port=22, username="root", password="", timeout=30)
    ssh.get_transport().auth_none("root")

    # kill watchdog_otaser process
    stdin, stdout, stderr = ssh.exec_command(cmdstr)
    tmp = stdout.read().decode().strip('\n')
    print(tmp)
    print(device, cmdstr," pid is :", tmp[1:5])
    ssh.exec_command("kill " + tmp[1:5])
    print("kill process success")
    ssh.close()


def transfer_data(localpath, remotepath):
    # 传输NOA刷机包
    # 创建SFTP实例
    tran = paramiko.Transport(('192.168.2.28', 22))
    with suppress(paramiko.ssh_exception.AuthenticationException):
        tran.connect(username="root", password=None)
    tran.auth_none("root")
    sftp = paramiko.SFTPClient.from_transport(tran)
    print("transfer data start")

    sftp.put(localpath, remotepath, callback=printTotals)
    # 关闭连接
    tran.close()
    print("transfer data Finished")

def printTotals(transferred, toBeTransferred):
    # print("Transferred: {0}\tOut of: {1}".format(transferred, toBeTransferred))
    print('percent: {:.2f}%'.format(transferred / toBeTransferred * 100) )

def version_check(host_name,device,version):
    version_result=[]
    ssh = paramiko.SSHClient()
    # 创建一个ssh的白名单
    know_host = paramiko.AutoAddPolicy()
    # 加载创建的白名单
    ssh.set_missing_host_key_policy(know_host)
    with suppress(paramiko.ssh_exception.AuthenticationException):
        ssh.connect(hostname=host_name, port=22, username="root", password="")
    ssh.get_transport().auth_none("root")
    # input update cmd
    stdin, stdout, stderr = ssh.exec_command("date")
    tmp = stdout.read().decode().strip('\n')
    version_result.append(tmp)

    stdin, stdout, stderr = ssh.exec_command("cat /usr/bin/Version_info")
    tmp = stdout.read().decode().strip('\n')
    version_result.append(tmp)
    print(device, version_result)
    if tmp == version:
        print("ota update success")
        return True
    else:
        print("ota update failed")
        return False


if __name__=='__main__':
    i = 1
    J3_version ="1065"   #设定开始升级前，当前软件版本
    f = open("D:\ota\ota.txt", mode="w")
    while i <= 500:        #设定OTA测试次数
        if J3_version =="1068":
            transfer_data("D:\ota\V1065\pilot3_ota.zip","/map/pilot3_ota.zip")
            ota_exe("192.168.2.10", 'J3A')
            ota_exe("192.168.2.11", 'J3B')
            ota_exe("192.168.2.28", 'J3C')
            ota_cmd()
            version = "Board type:j3pilotm1 Date:Mon May 23 00:36:55 CST 2022; Version_Number:QV_1.0.6.5"  #输入版本号
            result1 = version_check("192.168.2.10", 'J3A',version)
            result2 = version_check("192.168.2.11", 'J3B',version)
            result3 = version_check("192.168.2.28", 'J3C',version)
            result_str = "This is "+ str(i) + " times OTA test ! ota from " +J3_version+" to target version success"
            J3_version = "1065"
        elif J3_version == "1065":
            transfer_data("D:\ota\V1068\pilot3_ota.zip","/map/pilot3_ota.zip")
            ota_exe("192.168.2.10", 'J3A')
            ota_exe("192.168.2.11", 'J3B')
            ota_exe("192.168.2.28", 'J3C')
            ota_cmd()
            version = "Board type:j3pilotm1 Date:Sun Jun  5 17:12:22 CST 2022; Version_Number:QV_1.0.6.8" #输入版本号
            result1 = version_check("192.168.2.10", 'J3A', version)
            result2 = version_check("192.168.2.11", 'J3B', version)
            result3 = version_check("192.168.2.28", 'J3C', version)
            result_str = "This is " + str(i) + "times OTA test ! ota from " + J3_version + " to target version success"
            J3_version = "1068"

        print("This is ", i, " times OTA test")

        if (result1 == False) or (result2 == False) or (result3 == False):  #若升级失败，则退出OTA，保留现场
            f.write("ota failed")
            f.write("\n")
            break
        else:
            f.write(result_str)
            f.write("\n")
        time.sleep(5)
        i += 1
    f.close()