# coding=utf-8
import re
import sys
import time
import argparse
import paramiko
import os
from contextlib import suppress

TestMode = 0


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", help="NOA Update package", required=True)
    parser.add_argument("-hu", help="hu is HUinterface", required=True)
    parser.add_argument("-mcu", help="mcu is mcu_update_tcp_arm64", required=True)
    args = parser.parse_args()
    return args


def printTotals(transferred, toBeTransferred):
    # print("Transferred: {0}\tOut of: {1}".format(transferred, toBeTransferred))
    print('percent: {:.2f}%'.format(transferred / toBeTransferred * 100))


def transfer_data_key(localpath, remotepath):
    # 传输NOA刷机包
    # 创建SFTP实例
    tran = paramiko.Transport(('172.31.206.4', 22))
    pkey = os.path.join(os.getcwd(), "script", "j3update", "key.txt")
    key = paramiko.RSAKey.from_private_key_file(pkey)
    with suppress(paramiko.ssh_exception.AuthenticationException):
        tran.connect(username="root", password="", pkey=key)
    sftp = paramiko.SFTPClient.from_transport(tran)

    sftp.put(localpath, remotepath, callback=printTotals)
    # 关闭连接
    tran.close()


def transfer_data(localpath, remotepath):
    global TestMode
    if TestMode == 1:
        transfer_data_key(localpath, remotepath)
        return
    # 传输NOA刷机包
    # 创建SFTP实例
    tran = paramiko.Transport(('172.31.206.4', 22))
    with suppress(paramiko.ssh_exception.AuthenticationException):
        tran.connect(username="root", password=None)
    tran.auth_none("root")
    sftp = paramiko.SFTPClient.from_transport(tran)

    sftp.put(localpath, remotepath, callback=printTotals)
    # 关闭连接
    tran.close()


def checkmode(ip, cmd):
    # TestMode is no pro key
    global TestMode
    try:
        # TestMode is pro key
        # 创建SSH对象
        ssh = paramiko.SSHClient()
        # 允许连接不在know_hosts文件中的主机
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 创建试试实例
        pkey = os.path.join(os.getcwd(), "script", "j3update", "key.txt")
        key = paramiko.RSAKey.from_private_key_file(pkey)
        with suppress(paramiko.ssh_exception.AuthenticationException):
            ssh.connect(hostname=ip, port=22, username="root", pkey=key)
        ssh.get_transport()
        # 执行命令
        stdin, stdout, stderr = ssh.exec_command(cmd)
        # 获取命令结果
        res, err = stdout.read(), stderr.read()
        result = res if res else err
        # print(result.decode())
        ssh.close()
        TestMode = 1 
    except Exception as e:
        # TestMode is No key
        # 创建SSH对象
        ssh = paramiko.SSHClient()
        # 允许连接不在know_hosts文件中的主机
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 创建试试实例
        with suppress(paramiko.ssh_exception.AuthenticationException):
            ssh.connect(hostname=ip, port=22, username="root", password="")
        ssh.get_transport().auth_none("root")
        # 执行命令
        stdin, stdout, stderr = ssh.exec_command(cmd)
        # 获取命令结果
        res, err = stdout.read(), stderr.read()
        result = res if res else err
        # print(result.decode())
        ssh.close()
        TestMode = 0


def ssh_exe_key(ip, cmd):
    # 创建SSH对象
    ssh = paramiko.SSHClient()
    # 允许连接不在know_hosts文件中的主机
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 创建试试实例
    pkey = os.path.join(os.getcwd(), "script", "j3update", "key.txt")
    key = paramiko.RSAKey.from_private_key_file(pkey)
    with suppress(paramiko.ssh_exception.AuthenticationException):
        ssh.connect(hostname=ip, port=22, username="root", pkey=key)
    ssh.get_transport()
    # 执行命令
    # stdin, stdout, stderr = ssh.exec_command(cmd, timeout=100, get_pty=True)
    shell = ssh.invoke_shell()
    shell.sendall("%s\n" % cmd)
    shell.sendall("exit\n")
    while True:
        data = shell.recv(2048000).decode()
        if not data:
            print("quit now")
            break
        print(data, end="")
    ssh.close()


def ssh_exe(ip, cmd):
    global TestMode
    if TestMode == 1:
        ssh_exe_key(ip, cmd)
        return
        # 创建SSH对象
    ssh = paramiko.SSHClient()
    # 允许连接不在know_hosts文件中的主机
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 创建试试实例
    with suppress(paramiko.ssh_exception.AuthenticationException):
        ssh.connect(hostname=ip, port=22, username="root", password="")
    ssh.get_transport().auth_none("root")
    # 执行命令
    # stdin, stdout, stderr = ssh.exec_command(cmd, timeout=100, get_pty=True)
    shell = ssh.invoke_shell()
    shell.sendall("%s\n" % cmd)
    shell.sendall("exit\n")
    while True:
        data = shell.recv(2048000).decode()
        if not data:
            print("quit now")
            break
        print(data, end="")
    ssh.close()


def ssh_check_version_key(host, cmd):
    # 创建SSH对象
    ssh = paramiko.SSHClient()
    # 允许连接不在know_hosts文件中的主机
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 创建试试实例
    pkey = os.path.join(os.getcwd(), "script", "j3update", "key.txt")
    key = paramiko.RSAKey.from_private_key_file(pkey)
    with suppress(paramiko.ssh_exception.AuthenticationException):
        ssh.connect(hostname=host, port=22, username="root", pkey=key)
    ssh.get_transport()
    # 执行命令
    stdin, stdout, stderr = ssh.exec_command(cmd)
    # 获取命令结果
    res, err = stdout.read(), stderr.read()
    result = res if res else err
    # print(result.decode())
    ssh.close()
    return result.decode()


def ssh_check_version(host, cmd):
    global TestMode
    if TestMode == 1:
        ret = ssh_check_version_key(host, cmd)
        return ret
    # 创建SSH对象
    ssh = paramiko.SSHClient()
    # 允许连接不在know_hosts文件中的主机
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 创建试试实例
    with suppress(paramiko.ssh_exception.AuthenticationException):
        ssh.connect(hostname=host, port=22, username="root", password="")
    ssh.get_transport().auth_none("root")
    # 执行命令
    stdin, stdout, stderr = ssh.exec_command(cmd)
    # 获取命令结果
    res, err = stdout.read(), stderr.read()
    result = res if res else err
    # print(result.decode())
    ssh.close()
    return result.decode()

def ssh_exe_mcu_key(ip,cmd):
    # 创建SSH对象
    ssh = paramiko.SSHClient()
    # 允许连接不在know_hosts文件中的主机
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 创建试试实例
    pkey = os.path.join(os.getcwd(), "script", "j3update", "key.txt")
    key = paramiko.RSAKey.from_private_key_file(pkey)
    with suppress(paramiko.ssh_exception.AuthenticationException):
        ssh.connect(hostname=ip, port=22, username="root", password="", pkey=key)
    ssh.get_transport()
    # 执行命令
    try:
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=100, get_pty=True)
        # 获取命令结果
        # res, err = stdout.read(), stderr.read()
        # result = res if res else err
        # print(result.decode())
        while True:
            line = stdout.readline()
            if not line:
                break
            print(line)
    except:
        Exception
    ssh.close()
def ssh_exe_mcu(ip, cmd):
    global TestMode
    if TestMode == 1:
        ssh_exe_mcu_key(ip, cmd)
        return
    # 创建SSH对象
    ssh = paramiko.SSHClient()
    # 允许连接不在know_hosts文件中的主机
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 创建试试实例
    with suppress(paramiko.ssh_exception.AuthenticationException):
        ssh.connect(hostname=ip, port=22, username="root", password="")
    ssh.get_transport().auth_none("root")
    # 执行命令
    try:
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=100, get_pty=True)
        # 获取命令结果
        # res, err = stdout.read(), stderr.read()
        # result = res if res else err
        # print(result.decode())
        while True:
            line = stdout.readline()
            if not line:
                break
            print(line)
    except:
        Exception
    ssh.close()


def main():
    args = parse_args()
    localfile_package = args.f
    localfile_HUinterface = args.hu
    localfile_mcu_update = args.mcu
    IP_host = "172.31.206.4"
    workspce = "/userdata/update_cf/"
    remotefile_package = "/%s/NOA_UPGRADE_M01B.zip" % workspce
    remotefile_HUinterface = "/%s/HUinterface" % workspce
    remotefile_mcu_update = "/%s/mcu_update_tcp_arm64" % workspce
    checkmode(IP_host, "ls")
    print(TestMode)
    userdata_raw_data = ssh_check_version(IP_host, "df | grep userdata")
    if int(userdata_raw_data.split()[3]) < 3145728:
        ssh_exe(IP_host, 'cd /userdata;ls | egrep -v "(ota|cache)" | xargs rm -rf;sync;echo $?')
    ssh_exe(IP_host, 'mkdir -p /%s;rm -rf /%s/*' % (workspce, workspce))
    print("upload NOA Update package")
    transfer_data(localfile_package, remotefile_package)
    print("upload J3 Flash tool")
    transfer_data(localfile_HUinterface, remotefile_HUinterface)
    ssh_exe(IP_host, 'chmod +x /%s/HUinterface' % workspce)
    print("upload MCU Flash tool")
    transfer_data(localfile_mcu_update, remotefile_mcu_update)
    ssh_exe(IP_host, 'chmod +x /%s/mcu_update_tcp_arm64' % workspce)
    print("Start brush J3......")
    ssh_exe(IP_host, "cd /%s;unzip -o NOA_UPGRADE_M01B.zip" % workspce)

    J3B_BSP_file = ssh_check_version(IP_host, "cd /%s;ls all_in_one_J3_*" % workspce)
    print("J3A_BSP Version_file: %s" % J3B_BSP_file.split(".zip")[0].split("all_in_one_J3_")[1])

    J3A_app_version_file = ssh_check_version(IP_host, "cd /%s;ls App_J3_1_*" % workspce)
    str_teem_J3A = J3A_app_version_file.split(".zip")[0]
    J3A_APP_Version = str_teem_J3A[9:]
    if J3A_APP_Version.startswith('V'):
        J3A_APP_Version = J3A_APP_Version[1:]
    #J3A_APP_Version = re.findall(r"App_J3_1_(\d+\.+\d+\.+\d+\.+\d)", J3A_app_version_file.split(".zip")[0])
    print("J3A_APP Version_file: %s" % J3A_APP_Version.split("_")[0])

    J3B_app_version_file = ssh_check_version(IP_host, "cd /%s;ls App_J3_2_*" % workspce)
    str_temp = J3B_app_version_file.split(".zip")[0]
    
    J3B_APP_Version = str_temp[9:]
    if J3B_APP_Version.startswith("V"):
        J3B_APP_Version = J3B_APP_Version[1:]
    print("J3B_APP Version_file: %s" % J3B_APP_Version.split("_")[0])

    MCU_file = ssh_check_version(IP_host, "cd /%s;ls NOA_TC397_BSW*_ota.s19" % workspce)
    print("BSW Version_file:%s " % MCU_file.split("_ota.s19")[0].split("_")[2].split("BSW")[1])
    print("ASW Version_file:%s " % MCU_file.split("_ota.s19")[0].split("_")[3].split("ASW")[1])
    ssh_exe(IP_host, "cd /%s;./HUinterface --upgrade /%s" % (workspce, workspce))
    q = "%"
    ssh_exe(IP_host, "cd /%s;while [ true ];do ./HUinterface --progress;sleep 1;"
                     "re=`./HUinterface --progress | awk -F ' ' \'{print $3}\' | awk -F '%s' '{print $1}'`;echo $re;"
                     "if [[ ${re} == 100 ]];then break;fi; done" % (workspce, q))
    ssh_exe(IP_host, "cd /%s;./HUinterface --reboot" % workspce)
    time.sleep(5)
    print("Start brush MCU......")
    checkmode(IP_host, "ls")
    print(TestMode)
    ssh_exe_mcu(IP_host, 'cd /%s;./mcu_update_tcp_arm64 -f NOA_TC397_BSW*_ota.s19' % workspce)

    print("Check version of J3A BSP")

    host_J3A = "172.31.206.4"
    checkmode(host_J3A, "ls")
    print(TestMode)
    J3A_BSP_version_data = ssh_check_version(host_J3A, "cat /etc/version")
    print("J3A_BSP Version_check: %s" % J3A_BSP_version_data.split(" ")[0])
    # print("Check version of J3A APP")
    J3A_app_version_data = ssh_check_version(host_J3A, "cat /mnt/adas-rt/version")
    print("J3A_APP Version_check: %s" % J3A_app_version_data.split("-")[0])

    # print("Check version of J3B BSP")
    host_J3B = "172.31.206.5"
    checkmode(host_J3B, "ls")
    print(TestMode)
    J3B_BSP_version_data = ssh_check_version(host_J3B, "cat /etc/version")
    print("J3B_BSP Version_check: %s" % J3B_BSP_version_data.split(" ")[0])
    # print("Check version of J3B APP")
    J3B_app_version_data = ssh_check_version(host_J3B, "cat /mnt/version")
    print("J3B_APP Version_check: %s" % J3B_app_version_data.split(",")[0].split("{")[1].split(":")[1])
    print("Check version of MCU")

    J3_mcu_version_data = ssh_check_version(host_J3A, "cd /%s;./mcu_update_tcp_arm64 -v version" % workspce)
    bsw_data = re.findall(r"mcu system version: (\S+\.+\S+\.+\S+\.+\S)", J3_mcu_version_data)
    bsw_version = []
    for data in bsw_data[0].split("."):
        bsw_version.append(hex2dec(data))
    str_bsw_version = '.'.join(bsw_version)
    print("BSW Version_check:%s " % str_bsw_version)

    asw_data = re.findall(r"mcu asw version: (\S+\.+\S+\.+\S+\.+\S)", J3_mcu_version_data)
    asw_version = []
    for data in asw_data[0].split("."):
        asw_version.append(hex2dec(data))
    str_asw_version = '.'.join(asw_version)
    print("ASW Version_check:%s " % str_asw_version)


def hex2dec(string_num):
    return str(int(string_num.upper(), 16))


class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


if __name__ == "__main__":
    sys.stdout = Unbuffered(sys.stdout)
    main()
