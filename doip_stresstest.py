import socket
import time
from contextlib import suppress
import os
import hashlib
import paramiko


DoIP_header=[0x02, 0xFD, 0x80, 0x01]
DoIP_actiheader=[0x02, 0xFD, 0x00, 0x06]
Source_address=[0x0E, 0x80]
Target_phyaddress=[0x10, 0xC2]
Target_funaddress=[0xE4, 0x00]
MCU = ("172.16.50.12",13400)
#MCU = ("192.168.2.10",13400)
User_data=[]
recv_data=""



def ParseBinarytoTXT():
    Txtfile="../新建文件夹 - 副本.txt"
    Txtfilehandle=open(Txtfile,"w")
    return Txtfilehandle

def Recodelog():
    localtime=time.strftime("%Y-%m-%d_%H_%M_%S",time.localtime())
    logfile="Bootloader_log\\Bootloader_log_"+localtime+".txt"
    #print(logfile)
    logfilehandle=open(logfile,"w")
        #logfile.write(s)
    return logfilehandle

def fprint(f,s):
    print(s)
    if(isinstance(s,str)==True):
        f.write(s)
        f.write("\n")


def CalcKeyFromSeed_BOOT_HZ(seedlist):
    BOOT_MASK=0x00847016
    isKeyArray=[0]*4
    wSeed = (seedlist[0]<<24)+(seedlist[1]<<16)+(seedlist[2]<<8)+seedlist[3]
    #fprint("wSeed",wSeed)
    wLastSeed = wSeed
    temp = (( BOOT_MASK & 0x00000800) >> 10) | ((BOOT_MASK & 0x00200000)>> 21)
    #fprint("temp",temp)
    if(temp == 0):
        wTemp = ((wSeed | 0x00ff0000) >> 16)
    elif(temp == 1):
        wTemp = ((wSeed | 0xff000000) >> 24) 
    elif(temp == 2):
        wTemp = ((wSeed | 0x0000ff00) >> 8) 
    else: 
        wTemp = (wSeed | 0x000000ff)
    #fprint("wTemp",wTemp)
    SB1 = (( BOOT_MASK & 0x000003FC) >> 2)
    #fprint("SB1",SB1)
    SB2 = ((( BOOT_MASK & 0x7F800000) >> 23) ^ 0xA5)
    #fprint("SB2",SB2)
    SB3 = ((( BOOT_MASK & 0x001FE000) >> 13) ^ 0x5A)
    #fprint("SB3",SB3)
    iterations = (((wTemp | SB1) ^ SB2) + SB3)
    #fprint("iterations",iterations)
    for jj in range(iterations):
        wTemp = int((wLastSeed ^ 0x40000000) / 0x40000000) ^ int((wLastSeed & 0x01000000) / 0x01000000) ^ int((wLastSeed & 0x1000) / 0x1000) ^ int((wLastSeed & 0x04) / 0x04) 
        wLSBit = (wTemp ^ 0x00000001)
        wLastSeed = (wLastSeed << 1)&0xFFFFFFFF
        wTop31Bits = (wLastSeed ^ 0xFFFFFFFE)&0xFFFFFFFF
        wLastSeed = (wTop31Bits | wLSBit)&0xFFFFFFFF
        if(jj==0x4c4b40):
            Transfer_Data_to_SOC3e()
        elif(jj==0x989680):
            Transfer_Data_to_SOC3e() 
        elif(jj==0xe4e1c0):
            Transfer_Data_to_SOC3e()
    
    if(BOOT_MASK & 0x00000001): 
        wTop31Bits = ((wLastSeed & 0x00FF0000) >>16) | ((wLastSeed ^ 0xFF000000) >> 8) | ((wLastSeed 
        ^ 0x000000FF) << 8) | ((wLastSeed ^ 0x0000FF00) <<16) 
    else:
        wTop31Bits = wLastSeed
    wTop31Bits = wTop31Bits ^ BOOT_MASK
    isKeyArray[0]=(wTop31Bits>>24)&0xff
    isKeyArray[1]=(wTop31Bits>>16)&0xff
    isKeyArray[2]=(wTop31Bits>>8)&0xff
    isKeyArray[3]=wTop31Bits&0xff 
    return isKeyArray
    
def Calculate_MD5(file):
    md5list=[]
    with open(file,"rb") as f:
        hashmd5=hashlib.md5()
        hashmd5.update(f.read())
        md5=hashmd5.hexdigest()
        for i in range(0,32,2):
            md5list.append(int(md5[i:i+2],16))
    return md5list
    
def ParseFile(file):
    numline=0
    numbyte=0
    n=0
    k=0
    Flist=[]
    Txtfilehandle=ParseBinarytoTXT()
    with open(file,"rb") as f:
        size = os.path.getsize(file)
        line = 0
        #fprint(fhandle,size)
        for i in range(size):
                data = f.read(1)  # 每次输出一个字节
                Flist.append(int(data[0]))
                Txtfilehandle.write(hex(int(data[0])))
                n=n+1
                k=k+1
                if(n==100):
                    Txtfilehandle.write('\n')
                    n=0
                if(k==1000000):
                    line += 1
                    print("prase file ", round((line*1000000/size)*100, 2), "%")
                    k=0
        print("prase file ", 100.00, "%")
        #print(Flist)           
        #fprint(len(f.readlines()))
        #for line in f.readlines():
            #for i in range(0,len(line)):
            #fprint(line.encode())
                #Flist.append(ord(line[i]))
            #for i in list1:
                #fprint(i)
                #fprint(int(i,16))
                #a=int(i,16)
                #fprint(a)
                #Flist.append(a)
                #numbyte+=1
            #numline+=1
        #fprint(numbyte) 
        #fprint(numline)
    f.close()
    Txtfilehandle.close()
    
    return Flist
    
'''def char2byte(ch):
   if ( ch >= '0' and ch <= '9'):
      val = ch - 0x30   
   if ( ch >= 'a' and ch <= 'f'):
      val = (ch - 'a') + 10
   if ( ch >= 'A' and ch <= 'F'):
      val = (ch - 'A') + 10     
   return val '''

def Transfer_Data_to_SOC3e():   
    List_data=DoIP_header+[0x00,0x00,0x00,0x06]+Source_address+Target_phyaddress+[0x3e,0x00]
    send_bytes=bytes(List_data)
    soc.send(send_bytes)
    soc.settimeout(5)
    recv_data=soc.recv(1024)

def Transfer_Data_to_SOC(fhandle,mode,head,string,byte_length):   
    global recv_data
    flag=0
    flag_error=0
    Npayload_length=len(User_data)+4
    #fprint(Npayload_length)
    Payload_length=[0]*4
    Payload_length[0]=(Npayload_length>>24)&0xff
    Payload_length[1]=(Npayload_length>>16)&0xff
    Payload_length[2]=(Npayload_length>>8)&0xff
    Payload_length[3]=(Npayload_length)&0xff
    if(mode=="phy"):
        List_data=DoIP_header+Payload_length+Source_address+Target_phyaddress+User_data
    elif(mode=="fun"):
        List_data=DoIP_header+Payload_length+Source_address+Target_funaddress+User_data
    else:
        fprint(fhandle,"mode is invalid")
        return
    #fprint(List_data)
    send_bytes=bytes(List_data)
    #fprint(fhandle,send_bytes)
    #fprint(send_bytes)
    soc.send(send_bytes)
    #soc.settimeout(5)
    try:
        recv_data=soc.recv(1024)
    except BaseException:#TimeoutError:BaseException:
        recv_data="0"
    #fprint(recv_data)
    print(recv_data)
    if(len(User_data)>1 and User_data[1]&0xf0==0x80 and User_data[0]!=0x36):
        send_data=""
        for i in User_data:
            send_data=send_data + hex(i)+" "
        send_data=send_data.rstrip().upper().replace("X","x")
        if(recv_data.find(bytes([0x02,0xfd,0x80,0x02]),0,4)!=-1):
            fprint(fhandle,"DOIP UDS Func Response Pass,Send Data:[%s]" % send_data)
        else:
            fprint(fhandle,"DOIP UDS Func Response Fail,Send Data:[%s]" % send_data)
    else:
        if(recv_data.find(bytes([0x02,0xfd,0x80,0x01]),13,18) != -1): # receive diag ACK(8002) and diag response(8001) one time
            offset=13
        elif (recv_data.find(bytes([0x02, 0xfd, 0x80, 0x01]), 15, 20) != -1): # receive NRC 78 and diag positive response one time
            offset = 15
            flag_error = 1
            recv_data = recv_data[27:]
        elif(recv_data.find(bytes([0x02,0xfd,0x80,0x01]),0,5) != -1):  # receive diagnostic response directly
            offset=0
            flag_error=1
            recv_data=recv_data[12:-13]
        else:
            offset=0
            recv_data=soc.recv(1024)
        #fprint(recv_data)
        if(list(recv_data[offset:offset+4])==head):
            fprint(fhandle,"SOC Response Head Pass")
        else:
            fprint(fhandle,"SOC Response Head Fail")
        
        while (recv_data[offset+12:offset+15] == bytes([0x7f, 0x31, 0x78])) or (recv_data[offset+12:offset+15] == bytes([0x7f, 0x2e, 0x78])) or (recv_data[offset+12:offset+15] == bytes([0x7f, 0x27, 0x78]))or (recv_data[offset+12:offset+15] == bytes([0x7f, 0x22, 0x78]))or (recv_data[offset+12:offset+15] == bytes([0x7f, 0x11, 0x78]))or (recv_data[offset+12:offset+15] == bytes([0x7f, 0x14, 0x78])):
            soc.settimeout(10)
            recv_data = soc.recv(1024)
            if recv_data[12] == User_data[0] + 0x40:
                recv_data=recv_data[12:]
                flag=1
                break
        if(flag!=1 and flag_error!=1):
            #print(list(recv_data))
            recv_data=recv_data[offset+12:]
        list_start=[]
        recv_data_new=[]
        receive_data=""
        for i in list(recv_data):
            #print(list(recv_data))
            #print(i)
            #print(hex(i))
            receive_data=receive_data+hex(i)+" "
        receive_data=receive_data.rstrip().upper().replace("X","x")
        for i in string.split(" "):
            list_start.append(eval(i))
        #fprint(fhandle,len(list_start))
        #fprint(fhandle,list(recv_data))
        
        for i in range(len(list_start)):
            recv_data_new.append(list(recv_data)[i])
            #recv_data_new.append(list(recv_data)[i])
        if(recv_data_new==list_start and len(recv_data)==byte_length):
            fprint(fhandle,"DOIP UDS Phy Response Pass,Expect Response Data:[%s],Real Response Data:[%s]" % (string,receive_data))
            if(len(User_data)==3):
                if(User_data[1]==0x01 and User_data[2]==0x07):
                    return list(recv_data)[-1]
                else:
                    return 1
            else:
                return 1
        else:
            fprint(fhandle,"DOIP UDS Phy Response Fail,Expect Response Data:[%s],Real Response Data:[%s]" % (string,receive_data))
            if(len(User_data)==3):
                if(User_data[1]==0x01 and User_data[2]==0x07):
                    return -1
                else:
                    return 0
            else:
                return 0
    
    
    
    
    
def UserData_36(fhandle,user_data,Flist):
    global User_data
    #Flist=ParseFile("IECU_BootLoader-刷MCU.bin")
    #fprint(fhandle,len(Flist))
    #fprint(Flist)
    offset_36=0
    #MaxDataLen=(recv_data[-3]<<8)+recv_data[-2]-2  #F002, 60KB
    MaxDataLen = (recv_data[-4] << 16) + (recv_data[-3] << 8) + recv_data[-2] - 2 #400002, 4MB
    if(len(Flist)%MaxDataLen != 0):
        BlockNum=int(len(Flist)/MaxDataLen) +1
    else:
        BlockNum=int(len(Flist)/MaxDataLen)
    Trans_User_data=user_data    
    for i in range(0,BlockNum):
        if(len(Flist)-i*MaxDataLen>0 and len(Flist)-i*MaxDataLen<MaxDataLen):
            #MaxDataLen=len(l)-i*MaxDataLen
            User_data=Trans_User_data+[((i+1)&0xff)]+Flist[offset_36:]
            #fprint(fhandle,User_data)
        else:
            User_data=Trans_User_data+[((i+1)&0xff)]+Flist[offset_36:offset_36+MaxDataLen]
            offset_36+=MaxDataLen
        #fprint(fhandle,len(User_data))
        #fprint(User_data)
        #fprint(bytes(User_data))
        Transfer_Data_to_SOC(fhandle,"phy",DoIP_header,"0x76",2)
    #fprint(fhandle,len(Flist))
        
'''def Check_DOIP_UDS_Res(string,byte_length):#"0x50 0x01"
    list_start=[]
    recv_data_new=[]
    for i in string.split(" "):
        list_start.append(eval(i))
    for i in range(len(list_start)):
        recv_data_new+=recv_data[i]
    if(list(recv_data_new)==list_start and len(recv_data)==byte_length):
        fprint("DOIP UDS Response ok")
        return 1
    else:
        fprint("DOIP UDS Response fail")
        retun 0'''
    
def Active_route(fhandle):
    Expect_0006 = [0x02, 0xFD, 0x00, 0x06] + [0] * 3 + [0x09] + Source_address + Target_phyaddress + [0x10] + [0] * 4
    # 0005
    send_list = [0x02, 0xfd, 0x00, 0x05] + [0] * 3 + [0x07] + Source_address + [0] * 5
    #fprint(bytes(send_list))
    soc.send(bytes(send_list))
    # 0006
    with suppress(ConnectionResetError):
        recv_data = soc.recv(1024)
        #fprint(recv_data)
        #fprint(list(recv_data))
    if len(recv_data) == 21:
        if(recv_data == bytes(Expect_0006)):
            fprint(fhandle,"DoIP Request Vehicle Routing Active 0006 Pass")
        else:
            fprint(fhandle,"DoIP Request Vehicle Routing Active 0006 Fail")
            
    #soc.close()

def Connect_Vehicle():
    socket.setdefaulttimeout(10)
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #print(soc.gettimeout())
    soc.settimeout(5)
    #print(soc.gettimeout())
    soc.connect(MCU)
    
    return soc
def UDPreq_vehicle(fhandle):
    #socket.setdefaulttimeout(5)
    udpsoc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    local_addr=("",65534)
    udpsoc.bind(local_addr)
    time.sleep(1)
    send_list=[0x02, 0xfd, 0x00, 0x03]+[0]*3+[0x11,0x4C,0x56,0x56,0x44,0x43,0x31,0x31,0x42,0x36,0x41,0x44,0x35,0x32,0x34,0x32,0x38,0x36]
    #fprint(bytes(send_list))
    udpsoc.sendto(bytes(send_list),MCU)
    time.sleep(2)
    receData,peerAddr=udpsoc.recvfrom(83)
    if(list(receData[:4])==[0x02,0xFD,0x00,0x04]):
        fprint(fhandle,"DoIP Request Vehicle Infomation 0004 Pass")
    else:
        fprint(fhandle,"DoIP Request Vehicle Infomation 0004 Fail")
    #fprint(receData)
    time.sleep(5)
    #udpsoc.close()
    
USERDATA = [
    [0x22, 0xF1, 0x87],
    [0x22, 0xF1, 0x8A],
    [0x22, 0xF1, 0x8C],
    [0x22, 0xF1, 0xD0],
    [0x22, 0xF1, 0x91],
    [0x22, 0xF1, 0x80],
    [0x22, 0xF1, 0xC0],
    [0x10, 0x83],
    [0x31, 0x01, 0x02, 0x03],
    [0x85, 0x82],
    [0x28, 0x83, 0x03],
    [0x10, 0x02],
    [0x27, 0x11],
    [0x27, 0x12],
    [0x2E, 0xF1, 0x99, 0x20, 0x23, 0x03, 0x24],
    [0x2E, 0xF1, 0x98, 0x01, 0x02, 0x03, 0x04, 0x05, 0x05, 0x06, 0x07, 0x08, 0x09],
    [0x38, 0x03, 0x00, 0x10, 0x3A, 0x2F, 0x75, 0x73, 0x65, 0x72, 0x64, 0x61, 0x74, 0x61, 0x00, 0x00, 0x00, 0x00
        , 0x00, 0x00, 0x00, 0x04, 0xc8, 0x00, 0x00, 0x00, 0xc8, 0x00, 0x00, 0x00],
    [0x36],
    [0x37],
    [0x31, 0x01, 0xFF, 0x01, 0x3A, 0x2F, 0x75, 0x73, 0x65, 0x72, 0x64, 0x61, 0x74, 0x61, 0x00, 0x00, 0x00, 0x00
        , 0x00, 0x00, 0x10],
    [0x31, 0x01, 0x02, 0x05],
    [0x22, 0x01, 0x07],
    [0x11, 0x01],
    [0x22, 0x01, 0x07],
    [0x10, 0x83],
    [0x28, 0x80, 0x03],
    [0x85, 0x81],
    [0x10, 0x81],
    [0x14, 0xFF, 0xFF, 0xFF],
    [0x22, 0xF1, 0x87],
    [0x22, 0xF1, 0x8A],
    [0x22, 0xF1, 0x8C],
    [0x22, 0xF1, 0xD0],
    [0x22, 0xF1, 0x91],
    [0x22, 0xF1, 0x80],
    [0x22, 0xF1, 0xC0]
]

def reprogram():
    while 1:
        if ping(MCU[0]):
            break

def version_check(host_name,device,version):
    version_result = []
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

    if device == "J3":
        stdin, stdout, stderr = ssh.exec_command("cat /usr/bin/Version_info")
        tmp = stdout.read().decode().strip('\n')
        version_result.append(tmp)
        #print(device, version_result)
        fprint(fhandle, device+ ":"+ str(version_result))
        if tmp == version:
            fprint(fhandle, "ota update success")
            #print("ota update success")
            return True
        else:
            fprint(fhandle,"ota update failed")
            #print("ota update failed")
            return False
    elif device == "app":
        stdin, stdout, stderr = ssh.exec_command("cat /app/version.json")
        tmp = stdout.read().decode().strip('\n')
        version_result.append(tmp)
        #print(device, version_result)
        fprint(fhandle, device+ ":"+str(version_result))
        if tmp == version:
            #print("ota update success")
            fprint(fhandle, "ota update success")
            return True
        else:
            #print("ota update failed")
            fprint(fhandle, "ota update failed")
        return False
    elif device == "mcu":
        stdin, stdout, stderr = ssh.exec_command("cat /tmp/mcu_version")
        tmp = stdout.read().decode().strip('\n')
        version_result.append(tmp[:8])
        #print(device, version_result)
        fprint(fhandle, device+ ":"+str(version_result))
        if tmp[:8] == version:
            #print("ota update success")
            fprint(fhandle, "ota update success")
            return True
        else:
            #print("ota update failed")
            fprint(fhandle, "ota update failed")
        return False

def create_file(host_name):
    ssh = paramiko.SSHClient()
    # 创建一个ssh的白名单
    know_host = paramiko.AutoAddPolicy()
    # 加载创建的白名单
    ssh.set_missing_host_key_policy(know_host)
    with suppress(paramiko.ssh_exception.AuthenticationException):
        ssh.connect(hostname=host_name, port=22, username="root", password="")
    ssh.get_transport().auth_none("root")
    # input update cmd
    chan = ssh.invoke_shell()
    print("1")
    chan.send("cd /userdata/ \n")
    print("2")
    chan.send("dd if=/dev/zero of=aa bs=1M count=1000 \n")
    time.sleep(20)
    print("1.0G created")
    ssh.close()

if __name__ == "__main__":
    MD5list=[]
    Flist=[]
    MD5list1=[]
    Flist1=[]
    MD5list2=[]
    Flist2=[]
    Insta_sta_flag=0
    fhandle=Recodelog()
    TestIndex=0
    #使用前先赋值
    SoftwareVersion="2" #当前版本，是文件1还是文件2对应的版本
    host = "172.16.50.12"
    Filename1 = "pilot3_ota.zip" #文件1的名字
    Filename2 = "pilot3_ota_1.zip" #文件2的名字
    DefaultSoftwareVersion1 = "1"
    DefaultSoftwareVersion2 = "2"
    StressTestNumber = 1000

    
    MD5list1=Calculate_MD5(Filename1)
    Flist1=ParseFile(Filename1)
    MD5list2=Calculate_MD5(Filename2)
    Flist2=ParseFile(Filename2)
    
    while(TestIndex<StressTestNumber): 
        if(SoftwareVersion==DefaultSoftwareVersion2):
            MD5list=MD5list1
            Flist=Flist1
            J3_version = 'Board type:j3dvb Date:Mon Jun 26 17:27:03 CST 2023; Version_Number:QV_1.0.3.8'
            app_version='{"platform": "EP32", "version": "V1.4.0_20230625_1030_rvg01x", "car": "ep32"}'
            mcu_version='04.00.02'
        elif(SoftwareVersion==DefaultSoftwareVersion1):
            MD5list=MD5list2
            Flist=Flist2
            J3_version = 'Board type:j3dvb Date:Mon Jun 26 18:12:31 CST 2023; Version_Number:QV_1.0.3.8'
            app_version = '{"platform": "EP32", "version": "V1.3.6_20230531_1742_lnpc7h", "car": "ep32"}'
            mcu_version = '03.00.12'
        else:
            MD5list=MD5list1
            Flist=Flist1

        fprint(fhandle,"++++++Stress Test Current Cycle:%d,Set Cycle:%d++++++\n" % (TestIndex,StressTestNumber))
        #create_file(host)
        UDPreq_vehicle(fhandle)
        soc=Connect_Vehicle()
        Active_route(fhandle)
        index = 0
    #fhandle=Recodelog()
    #while(1):  
        Insta_sta_flag=0

        User_data = USERDATA[index]
        if (Transfer_Data_to_SOC(fhandle, "phy", DoIP_header,
                                 "0x62 0xF1 0x87 0x53 0x33 0x32 0x2D 0x33 0x36 0x30 0x32 0x30 0x31 0x31 0x20 0x20",
                                 16) == 0):  # 22 F1 87
            break
        index += 1

        User_data = USERDATA[index]
        if (Transfer_Data_to_SOC(fhandle, "phy", DoIP_header,
                                 "0x62 0xF1 0x8A 0x39 0x53 0x58",
                                 6) == 0):  # 22 F1 8A
            break
        index += 1

        User_data = USERDATA[index]
        if (Transfer_Data_to_SOC(fhandle, "phy", DoIP_header,
                                 "0x62 0xF1 0x8C 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00",
                                 21) == 0):  # 22 F1 8C
            # break
            pass
        index += 1

        User_data = USERDATA[index]
        if (Transfer_Data_to_SOC(fhandle, "phy", DoIP_header,
                                 "0x62 0xF1 0xD0 0x53 0x33 0x32 0x2D 0x33 0x36 0x30 0x34 0x39 0x39 0x39 0x20 0x20",
                                 16) == 0):  # 22 F1 D0
            break
        index += 1

        User_data = USERDATA[index]
        if (Transfer_Data_to_SOC(fhandle, "phy", DoIP_header,
                                 "0x62 0xF1 0x91 0x48 0x31 0x2E 0x33 0x30",
                                 8) == 0):  # 22 F1 91
            break
        index += 1

        User_data = USERDATA[index]
        if (Transfer_Data_to_SOC(fhandle, "phy", DoIP_header,
                                 "0x62 0xF1 0x80 0x30 0x32 0x2E 0x30 0x30 0x2E 0x30 0x34",
                                 11) == 0):  # 22 F1 80
            break
        index += 1

        User_data = USERDATA[index]
        if (Transfer_Data_to_SOC(fhandle, "phy", DoIP_header,
                                 "0x62 0xF1 0xC0 0x30 0x33 0x2E 0x30 0x30 0x2E 0x31 0x32",
                                 11) == 0):  # 22 F1 C0
            #break
            pass
        index += 1

        User_data=USERDATA[index]
        if(Transfer_Data_to_SOC(fhandle,"fun",DoIP_actiheader,"0x10",9)==0):#10 83
            break
        index +=1
        #fprint(index)
        
        User_data=USERDATA[index]
        if(Transfer_Data_to_SOC(fhandle,"phy",DoIP_header,"0x71 0x01 0x02 0x03 0x02",5)==0):#31 01 02 03
            break
        index +=1
            
        User_data=USERDATA[index]
        if(Transfer_Data_to_SOC(fhandle,"fun",DoIP_header,"",5)==0):#85 82
            break
        index +=1

        User_data=USERDATA[index]
        if(Transfer_Data_to_SOC(fhandle,"fun",DoIP_header,"",5)==0):#28 81 03
            break
        index +=1

        User_data=USERDATA[index]
        if(Transfer_Data_to_SOC(fhandle,"phy",DoIP_header,"0x50 0x02 0x00 0x32 0x01 0xF4",6)==0):#10 02
            break
        index +=1
        
        User_data=USERDATA[index]
        if(Transfer_Data_to_SOC(fhandle,"phy",DoIP_header,"0x67 0x11",6)==0):#27 11
            break
        index +=1
        #fprint(recv_data[2:])
        #send_list=[x for x in recv_data[2:]]
        #fprint(send_list)
        key_list=CalcKeyFromSeed_BOOT_HZ(list(recv_data[2:]))
        User_data=USERDATA[index]+key_list
        if(Transfer_Data_to_SOC(fhandle,"phy",DoIP_header,"0x67 0x12",2)==0):#27 12
            break
        index +=1
        
        User_data=USERDATA[index]
        if(Transfer_Data_to_SOC(fhandle,"phy",DoIP_header,"0x6E 0xF1 0x99",3)==0):#2E F1 99
            break
        index +=1

        User_data=USERDATA[index]
        if(Transfer_Data_to_SOC(fhandle,"phy",DoIP_header,"0x6E 0xF1 0x98",3)==0):#2E F1 98
            break
        index +=1

        User_data=USERDATA[index]
        if(Transfer_Data_to_SOC(fhandle,"phy",DoIP_header,"0x78 0x03 0x02 0xF0 0x02 0x00",6)==0):#38 01 00 10
            #fprint(fhandle,list(recv_data))
            #break
            pass
        index +=1
        
        User_data=USERDATA[index]
        if(UserData_36(fhandle,User_data,Flist)==0):#36
            break
        index +=1
        
        User_data=USERDATA[index]
        if(Transfer_Data_to_SOC(fhandle,"phy",DoIP_header,"0x77",1)==0):#37
            break
        index +=1

        User_data=USERDATA[index]+MD5list
        if(Transfer_Data_to_SOC(fhandle,"phy",DoIP_header,"0x71 0x01 0xFF 0x01",5)==0):#31 01 FF 01
            break
        index +=1
        
        User_data=USERDATA[index]
        if(Transfer_Data_to_SOC(fhandle,"phy",DoIP_header,"0x71 0x01 0x02 0x05",5)==0):#31 01 02 05
            break
        index +=1
        
        User_data=USERDATA[index]
        while(1):
            result=Transfer_Data_to_SOC(fhandle,"phy",DoIP_header,"0x62 0x01 0x07",4)
        #if(Transfer_Data_to_SOC(fhandle,"phy",DoIP_header,"0x62 0x01 0x07",4)==0):#22 01 07
            if(result==0):
                break
            elif(result==2):
                time.sleep(2)
            elif(result==1):
                fprint(fhandle,"Update soteware Fail,Feedback value:0x01")
                Insta_sta_flag=1
                break
            else:
                fprint(fhandle,"Expect Data Fail/invalid Feedback value")
                Insta_sta_flag=1
                break
        if(Insta_sta_flag==1):
            break
        index +=1
        
        User_data=USERDATA[index]
        if(Transfer_Data_to_SOC(fhandle,"phy",DoIP_header,"0x51 0x01",2)==0):#11 01
            break
            #pass
        index +=1
        
        time.sleep(20)
        soc=Connect_Vehicle()
        Active_route(fhandle)
        User_data = USERDATA[index]  # 22 01 07 for sofaware activation status check
        while (1):
            result = Transfer_Data_to_SOC(fhandle, "phy", DoIP_header, "0x62 0x01 0x07", 4)
            # if(Transfer_Data_to_SOC(fhandle,"phy",DoIP_header,"0x62 0x01 0x07",4)==0):#22 01 07
            if (result == 0):
                break
            elif (result == 2):
                time.sleep(1)
            elif (result == 1):
                fprint(fhandle, "Activate soteware Fail,Feedback value:0x01")
                Insta_sta_flag = 1
                break
            else:
                fprint(fhandle, "Software activation Expect Data Fail/invalid Feedback value")
                Insta_sta_flag = 1
                break
        if (Insta_sta_flag == 1):
            break
        index += 1

        User_data=USERDATA[index]
        if(Transfer_Data_to_SOC(fhandle,"fun",DoIP_header,"",5)==0):#10 83
            break
        index +=1
        
        User_data=USERDATA[index]
        if(Transfer_Data_to_SOC(fhandle,"fun",DoIP_header,"",5)==0):#28 80 03
            break
        index +=1
        
        User_data=USERDATA[index]
        if(Transfer_Data_to_SOC(fhandle,"fun",DoIP_header,"",5)==0):#85 81
            break
        index +=1
        
        User_data=USERDATA[index]
        if(Transfer_Data_to_SOC(fhandle,"fun",DoIP_header,"",5)==0):#10 81
            break
        index +=1

        User_data=USERDATA[index]
        if(Transfer_Data_to_SOC(fhandle,"phy",DoIP_header,"0x54",1)==0):#14 FF FF FF
            break
            #pass
        index +=1

        User_data = USERDATA[index]
        if (Transfer_Data_to_SOC(fhandle, "phy", DoIP_header,
                                 "0x62 0xF1 0x87 0x53 0x33 0x32 0x2D 0x33 0x36 0x30 0x32 0x30 0x31 0x31 0x20 0x20",
                                 16) == 0):  # 22 F1 87
            break
        index += 1

        User_data = USERDATA[index]
        if (Transfer_Data_to_SOC(fhandle, "phy", DoIP_header,
                                 "0x62 0xF1 0x8A 0x39 0x53 0x58",
                                 6) == 0):  # 22 F1 8A
            break
        index += 1

        User_data = USERDATA[index]
        if (Transfer_Data_to_SOC(fhandle, "phy", DoIP_header,
                                 "0x62 0xF1 0x8C 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00",
                                 21) == 0):  # 22 F1 8C
            # break
            pass
        index += 1

        User_data = USERDATA[index]
        if (Transfer_Data_to_SOC(fhandle, "phy", DoIP_header,
                                 "0x62 0xF1 0xD0 0x53 0x33 0x32 0x2D 0x33 0x36 0x30 0x34 0x39 0x39 0x39 0x20 0x20",
                                 16) == 0):  # 22 F1 D0
            break
        index += 1

        User_data = USERDATA[index]
        if (Transfer_Data_to_SOC(fhandle, "phy", DoIP_header,
                                 "0x62 0xF1 0x91 0x48 0x31 0x2E 0x33 0x30",
                                 8) == 0):  # 22 F1 91
            break
        index += 1

        User_data = USERDATA[index]
        if (Transfer_Data_to_SOC(fhandle, "phy", DoIP_header,
                                 "0x62 0xF1 0x80 0x30 0x32 0x2E 0x30 0x30 0x2E 0x30 0x34",
                                 11) == 0):  # 22 F1 80
            break
        index += 1

        User_data = USERDATA[index]
        if (Transfer_Data_to_SOC(fhandle, "phy", DoIP_header,
                                 "0x62 0xF1 0xC0 0x30 0x33 0x2E 0x30 0x30 0x2E 0x31 0x32",
                                 11) == 0):  # 22 F1 C0
            #break
            pass
        index += 1


        result1 = version_check(host, 'J3', J3_version)
        result2 = version_check(host, 'app', app_version)
        result3 = version_check(host, 'mcu', mcu_version)

        if (result1 == False) or (result2 == False) or (result3 == False):
            break
        else:
            if SoftwareVersion==DefaultSoftwareVersion1:
                SoftwareVersion=DefaultSoftwareVersion2
            else:
                SoftwareVersion = DefaultSoftwareVersion1
        fprint(fhandle, "++++++Stress Test Current Cycle:%d, end rrSet Cycle:%d++++++\n" % (TestIndex, StressTestNumber))
        TestIndex=TestIndex+1
        time.sleep(6)
        #break
    fhandle.close()







  
    
    
    
    