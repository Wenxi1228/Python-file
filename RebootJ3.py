from contextlib import suppress
import time

import paramiko


def reboot_req():
    ssh = paramiko.SSHClient()
    # 创建一个ssh的白名单
    know_host = paramiko.AutoAddPolicy()
    # 加载创建的白名单
    ssh.set_missing_host_key_policy(know_host)
    with suppress(paramiko.ssh_exception.AuthenticationException):
        ssh.connect(hostname="192.168.2.28", port=22, username="root", password="")
    ssh.get_transport().auth_none("root")

    # ssh.exec_command("cd /map")
    # print("1")
    # stdin, stdout, stderr = ssh.exec_command("./ota_testAPI /")
    # print("3")
    # time.sleep(2)
    # print(stdout.read().decode())
    # #ssh.exec_command("date")
    # stdin, stdout, stderr = ssh.exec_command("date")
    # print(stdout.read().decode())
    # print("2")
        #input update cmd
    chan=ssh.invoke_shell()
    chan.send("cd /map \n")
    time.sleep(1)
    print(chan.recv(100).decode())

    chan.send("./ota_testAPI 1 \n")
    time.sleep(10)
    print(chan.recv(100).decode())

    chan.send("./ota_testAPI 0 \n")
    #chan.send("fdisk -l \n")
    time.sleep(3)
    print(chan.recv(100).decode())
    print(chan.recv(99999).decode())
    ssh.close()

if __name__=='__main__':
    i = 0
    while i < 500:
        reboot_req()
        i += 1
        print("this is ",i, " times reboot")
        time.sleep(7)