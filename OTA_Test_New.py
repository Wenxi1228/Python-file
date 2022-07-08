import time
from contextlib import suppress
import paramiko

# 创建一个ssh的客户端，用来连接服务器
def ota_exe(host_name, device):
    if device =="J3A":
        proc_kill(host_name,device, "ps |grep ota-watchdog")
        proc_kill(host_name, device, "ps |grep ota-log-udp-sender")
        proc_kill(host_name, device, "ps |grep otaservice")
    elif device =="J3B":
        proc_kill(host_name, device, "ps |grep ota-watchdog")
        proc_kill(host_name, device, "ps |grep ota-log-udp-sender")
        proc_kill(host_name, device, "ps |grep otaservice")
    else:
        # proc_kill(host_name, device, "ps |grep ota-watchdog")
        # proc_kill(host_name, device, "ps |grep ota-log-udp-sender")
        # proc_kill(host_name, device, "ps |grep otaservice")
        proc_kill(host_name, device, "ps | grep agent-watchdog")
        proc_kill(host_name, device, "ps | grep agent-log-udp-sender")
        proc_kill(host_name, device, "ps | grep agent_module")

def otaservice(device_ID, host_name):
    ssh = paramiko.SSHClient()
    # 创建一个ssh的白名单
    know_host = paramiko.AutoAddPolicy()
    # 加载创建的白名单
    ssh.set_missing_host_key_policy(know_host)
    with suppress(paramiko.ssh_exception.AuthenticationException):
        ssh.connect(hostname=host_name, port=22, username="root", password="")
    ssh.get_transport().auth_none("root")
        #input update cmd
    chan=ssh.invoke_shell()
    if device_ID == "J3A":
        print("1")
        chan.send("cd /usr/ota/otaservice/ \n")
        time.sleep(1)
        print("2")
        chan.send("./otaservice ./config/ OTA-J3A 4 > /map/otaservice_J3A.log 2>&1 & \n")
    elif device_ID == "J3B":
        print("1")
        chan.send("cd /usr/ota/otaservice/ \n")
        time.sleep(1)
        print("2")
        chan.send("./otaservice ./config/ OTA-J3B 4 > /map/otaservice_J3B.log 2>&1 & \n")
    else:
        print("1")
        chan.send("cd /usr/ota/otaservice/ \n")
        time.sleep(1)
        print("2")
        chan.send("./otaservice ./config/ OTA-J3C 4 > /map/otaservice_J3C.log 2>&1 & \n")
    ssh.close()

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
    while i < 110:   #开始升级后等待240s
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

def app_version_check(host_name,device,version):
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

    if device=="J3C":
        stdin, stdout, stderr = ssh.exec_command("cat /app/autodrive/version.json")
        tmp = stdout.read().decode().strip('\n')
        version_result.append(tmp)
        print(device, version_result)
        if tmp == version:
            print("ota update success")
            return True
        else:
            print("ota update failed")
            return False
    else:
        stdin, stdout, stderr = ssh.exec_command("cat /app/app_version")
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
    J3_version ="1079x"   #设定开始升级前，当前软件版本
    f = open("D:\ota\ota.txt", mode="w")
    while i <= 500:        #设定OTA测试次数
        if J3_version =="1079":
            transfer_data("D:\ota\V1079x\pilot3_ota.51","/map/pilot3_ota.51")
            #ota_exe("192.168.2.10", 'J3A')
            #ota_exe("192.168.2.11", 'J3B')
            ota_exe("192.168.2.28", 'J3C')
            # otaservice("J3A", "192.168.2.10")
            # otaservice("J3B", "192.168.2.11")
            # otaservice("J3C", "192.168.2.28")
            ota_cmd()
            #version = "Board type:j3pilotm1 Date:Fri Jun 10 00:03:10 CST 2022; Version_Number:QV_1.0.7.0"  #输入版本号
            version = "Board type:j3pilotm1 Date:Thu Jul  7 18:58:07 CST 2022; Version_Number:QV_1.0.7.9"
            result1 = version_check("192.168.2.10", 'J3A',version)
            result2 = version_check("192.168.2.11", 'J3B',version)
            result3 = version_check("192.168.2.28", 'J3C',version)
            result4 = app_version_check("192.168.2.10", 'J3A', "V4.6.1-20220626-0432")
            result5 = app_version_check("192.168.2.11", 'J3B', "V4.6.1-20220626-0433")
            result6 = app_version_check("192.168.2.28", 'J3C', '{"version": "v1.0.7.5_r4.0.0_r3.5.6_20220627_1853", "platform": "J3"}')
            result_str = "This is "+ str(i) + " times OTA test ! ota from " +J3_version+" to target version success"
            J3_version = "1079x"
        elif J3_version == "1079x":
            transfer_data("D:\ota\V1079\pilot3_ota.51","/map/pilot3_ota.51")
            # ota_exe("192.168.2.10", 'J3A')
            # ota_exe("192.168.2.11", 'J3B')
            ota_exe("192.168.2.28", 'J3C')
            # otaservice("J3A", "192.168.2.10")
            # otaservice("J3B", "192.168.2.11")
            # otaservice("J3C", "192.168.2.28")
            ota_cmd()
            #version = "Board type:j3pilotm1 Date:Mon May 30 17:05:31 CST 2022; Version_Number:QV_1.0.6.7" #输入版本号
            version = "Board type:j3pilotm1 Date:Thu Jul  7 18:58:07 CST 2022; Version_Number:QV_1.0.7.9"
            result1 = version_check("192.168.2.10", 'J3A', version)
            result2 = version_check("192.168.2.11", 'J3B', version)
            result3 = version_check("192.168.2.28", 'J3C', version)
            result4 = app_version_check("192.168.2.10", 'J3A', "V4.6.5-20220705-1412")
            result5 = app_version_check("192.168.2.11", 'J3B', "V4.6.5-20220705-1413")
            result6 = app_version_check("192.168.2.28", 'J3C', '{"version": "v1.0.7.8_r4.0.7_r3.5.6_20220705_2340", "platform": "J3"}')
            result_str = "This is " + str(i) + " times OTA test ! ota from " + J3_version + " to target version success"
            J3_version = "1079"

        # if J3_version =="1064":
        #     transfer_data("D:\ota\V1070\pilot3_ota.zip","/map/pilot3_ota.zip")
        #     ota_exe("192.168.2.10", 'J3A')
        #     ota_exe("192.168.2.11", 'J3B')
        #     ota_exe("192.168.2.28", 'J3C')
        #     ota_cmd()
        #     version = "Board type:j3pilotm1 Date:Mon May 30 17:05:31 CST 2022; Version_Number:QV_1.0.6.7"  #输入版本号
        #     result1 = version_check("192.168.2.10", 'J3A',version)
        #     result2 = version_check("192.168.2.11", 'J3B',version)
        #     result3 = version_check("192.168.2.28", 'J3C',version)
        #     result_str = "This is "+ str(i) + " times OTA test ! ota from " +J3_version+" to target version success"
        #     J3_version = "1067"
        # elif J3_version == "1067":
        #     transfer_data("D:\ota\V1064\pilot3_ota.zip","/map/pilot3_ota.zip")
        #     ota_exe("192.168.2.10", 'J3A')
        #     ota_exe("192.168.2.11", 'J3B')
        #     ota_exe("192.168.2.28", 'J3C')
        #     ota_cmd()
        #     #version = "Board type:j3pilotm1 Date:Mon May 30 17:05:31 CST 2022; Version_Number:QV_1.0.6.7" #输入版本号
        #     version = "Board type:j3pilotm1 Date:Fri May 13 16:18:22 CST 2022; Version_Number:QV_1.0.6.4"
        #     result1 = version_check("192.168.2.10", 'J3A', version)
        #     result2 = version_check("192.168.2.11", 'J3B', version)
        #     result3 = version_check("192.168.2.28", 'J3C', version)
        #     result_str = "This is " + str(i) + " times OTA test ! ota from " + J3_version + " to target version success"
        #     J3_version = "1064"


        print("This is ", i, " times OTA test")
        if (result1 == False) or (result2 == False) or (result3 == False) or (result4 == False) or (result5 == False) or (result6 == False):  #若升级失败，则退出OTA，保留现场
            f.write("ota failed")
            f.write("\n")
            break
        else:
            f.write(result_str)
            f.write("\n")

        time.sleep(5)
        i += 1
    f.close()