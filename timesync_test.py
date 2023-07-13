from test_case import TestCase
from common_services import read_software_version, read_j3_date
from datetime import datetime
from time import sleep
import time
import random
from candata import candata
from ssh_client import ssh_client

def help_info_timesync():
    print("The command format is : ")
    print("hads_testsuit.exe timesync [option_1] [option_2] ... ... [option_n]")
    print("")
    print("Functions:")
    print("-v                    Read the version of the tool")
    print("-h                    Show help information.")
    print("-t  times             Times for timesync test.Default is 100")
    print("eg:                   hads_testsuit.exe timesync")
    
class timesync_testcases(TestCase): 
    def __init__(self):
        self.testcnt = 0
        self.successcnt = 0
        self.failcnt = 0
        self.logdict = dict()
        self.resultdict = dict()

        self.ssha = None
        self.sshb = None
        self.sshc = None
        self.canfd = None
        self.ethxcp = None

        self.lads_canfd = None
    
        self.mcu_ver = ""
        self.j3a_ver = ""
        self.j3b_ver = ""
        self.j3c_ver = ""
        self.prelog = dict()

        self.timesynccnt = 0

    def update_info(self):
        pass

    def print_info(self):
        pass

    def runPreparation(self):
        self.canfd = candata("vector", '3', 500000, 2000000, 0x735, 0x73d)
        self.lads_canfd = candata("vector", '2', 500000, 2000000, 0x735, 0x73d)
        #cdta.send_wakeup()
        self.canfd.send_wakeup()
        sleep(10)

        while ((self.ssha == None) or (self.sshb == None) or (self.sshc == None)):
            if self.ssha == None:
                try:
                    self.ssha = ssh_client("192.168.2.10", None)
                except Exception as e:
                    print(e)

            if self.sshb == None:
                try:                
                    self.sshb = ssh_client("192.168.2.11", None)
                except Exception as e:
                    print(e)

            if self.sshc == None:
                try:
                    self.sshc = ssh_client("192.168.2.28", None)    
                except Exception as e:
                    print(e)
       
        #read software version
        ret = read_software_version(self.ssha, self.sshb, self.sshc, self.canfd)
        self.mcu_ver = ret[0]
        self.j3a_ver = ret[2]
        self.j3b_ver = ret[4]
        self.j3c_ver = ret[6]

        self.canfd.stop_periodic_messages()
        while(self.canfd.bus_empty() == False):
            #sleep(1)
            pass 
        self.canfd.flush_txmsg()
        sleep(10)

    def runTest(self):
        dlist = [None, None, None]
        dslist = ["J3A","J3B","J3C"]
        iplist = ["192.168.2.10", "192.168.2.11", "192.168.2.28"]
        j3_time = ["", "", ""]
        synclist = [False, False, False]
        __tc_cnt = 0
        __start_time = 0
        tmplog = []

        while(__tc_cnt<self.timesynccnt):
            
            __tc_cnt = __tc_cnt +1
            tmplist = [2.9,3.0,3.1,3.2,3.3,3.4,3.5,3.8,3.9,4.0,4.1,4.2,4.3,4.4]
            __start_time =  tmplist[random.randint(0,13)]
            tmpTitle = "Test Case "+str(__tc_cnt)+"  : Simulate to send wakeup message after "+str(__start_time)+" s."
            print(tmpTitle)
            self.pushtitle(tmpTitle)
            tmploglist =[]
            j3_time = ["", "", ""]
            dlist = [None, None, None]
            tmplog = []

            tmpstr = "Send wakeup to start Test Cases...... ."+str(datetime.now()) 
            print(tmpstr)
            tmploglist.append(tmpstr)
            self.canfd.flush_txmsg()
            __start = time.time()
            self.canfd.send_wakeup()    
            
            __localtime= time.localtime(time.time())
            __can_time_sync_cmd = [0x05, 0x29, 0x06, 0x08, 0x00, 0x00,0x00, 0x00,0x00, 0x00,0x00, 0x00]
            __can_time_sync_cmd[5]  = (((__localtime.tm_mon)<<4)&0xF0)
            __can_time_sync_cmd[6]  = ((__localtime.tm_mday)&0x1F)
            __can_time_sync_cmd[7]  = ((__localtime.tm_year-2000)&0xFF)
            __can_time_sync_cmd[8]  = ((__localtime.tm_min)&0x3F)
            __can_time_sync_cmd[9]  = ((__localtime.tm_sec)&0x3F)
            __can_time_sync_cmd[10] = ((__localtime.tm_hour)&0x1F)

            self.lads_canfd.flush_txmsg()

            __end = time.time()
            while((__end-__start)<(__start_time)):
                __end = time.time()
            self.lads_canfd.send_timesync(0x476, __can_time_sync_cmd)

            tmpstr = "Wait "+str(__start_time)+" s and start to send timesync message"+str(datetime.now())
            print(tmpstr)
            tmploglist.append(tmpstr)
            
            __start = time.time()
            __end = time.time()
            while((__end-__start)<240):
                for i in range(3):
                    try:
                        if synclist[i] == False:
                            if dlist[i] == None: 
                                dlist[i] = ssh_client(iplist[i], 2)
                            else:
                                tmplog = read_j3_date(dlist[i], "date", dslist[i])

                                for tmpstr in tmplog[0]:
                                    print(tmpstr)
                                tmploglist = tmploglist+tmplog[0]
                                j3_time[i] = tmplog[1]

                                if ((__start_time <3.6) and (int(j3_time[i].split(" ")[-1]) == 2022)):
                                    synclist[i] = True
                                elif ((__start_time >=3.6) and (int(j3_time[i].split(" ")[-1]) == 2020)):
                                    synclist[i] = True
                                else:
                                    synclist[i] = False

                    except Exception as e:
                        pass
                        #ssh_clienta = None
                        
                        print(e)
                print(synclist)
                if((synclist[0] == True)and(synclist[1] == True)and(synclist[2] == True)):
                    break
                else:
                    __end = time.time()
                    sleep(1)
                    

            if((synclist[0] == True)and(synclist[1] == True)and(synclist[2] == True)):
                self.pushresult(tmpTitle, "Pass")
                self.successcnt = self.successcnt +1
            else:
                self.pushresult(tmpTitle, "Fail")
                self.failcnt = self.failcnt+1
                if(synclist[2] == False):
                    tmpstr = "After 240s, Time on J3C............................"+j3_time[2]
                    print(tmpstr)
                    tmploglist.append(tmpstr)

                if(synclist[1] == False):
                    tmpstr = "After 240s, Time on J3B............................"+j3_time[1]
                    print(tmpstr)
                    tmploglist.append(tmpstr)

                if(synclist[0] == False):
                    tmpstr = "After 240s, Time on J3A............................"+j3_time[0]
                    print(tmpstr)
                    tmploglist.append(tmpstr)

            synclist = [False, False, False]

            tmpstr = "Stop wakeup message to make controller sleep."+str(datetime.now()) 
            
            print(tmpstr)
            tmploglist.append(tmpstr)                            

            self.canfd.stop_periodic_messages()
            self.lads_canfd.stop_periodic_messages()
            
            while(self.canfd.bus_empty() == False):
                #sleep(1)
                pass

            while(self.lads_canfd.bus_empty() == False):
                #sleep(1)
                pass            

            tmpstr = "No CAN Message received from HADS."+str(datetime.now()) 
            
            print(tmpstr)
            tmploglist.append(tmpstr)                            

            self.pushlog(tmpTitle, tmploglist)
            sleep(10)  

    def genReport(self):
        report = []

        report.append("<!DOCTYPE html>")
        report.append("<html>")
        report.append("<head>")
        report.append("<meta charset=\"utf-8\">")
        report.append("</head>")
        report.append("<body>")
        report.append("<H1>Kill spi_service Test Report</H1>")
        report.append("</br>")
        report.append("<H2>Software Version</H2>")
        report.append("<ul>")
        report.append("<li><em>MCU Software Version:     "+self.mcu_ver+"</em></li>")
        report.append("<li><em>J3A Software Version:     "+self.j3a_ver+"</em></li>")
        report.append("<li><em>J3B Software Version:     "+self.j3b_ver+"</em></li>")
        report.append("<li><em>J3C Software Version:     "+self.j3c_ver+"</em></li>")
        report.append("</ul>")
        report.append("</br>")

        report.append("<H2>Test Summary</H2>")
        report.append("<ul>")
        report.append("<li><em>Kill spi_service Test cases:     "+str(self.testcnt)+"</em></li>")
        report.append("<li><em>Success Test cases:   "+str(self.successcnt)+"</em></li>")
        report.append("<li><em>Failed Test cases:    "+str(self.failcnt)+"</em></li>")
        report.append("<ul>")

        for tmpkey in self.resultdict.keys():
            if(self.resultdict[tmpkey] != "Pass"):
                tmpac = tmpkey.replace(" ","_")
                acstr = "#ac_"+tmpac
                report.append("<li><a href=\""+acstr+"\">"+ tmpkey+"</a></li>")

        report.append("</ul>")
        report.append("</ul>")

        for tmpkey in self.logdict.keys():
            tmpac = tmpkey.replace(" ","_")
            acstr = "ac_"+tmpac
            report.append("<H3 id="+acstr+" name="+acstr+">"+tmpkey+"</H3>")
            if(self.resultdict[tmpkey] == "Pass"):
                report.append("<p><em>Test Result: Pass</em></p>")
            else:
                report.append("<p><em>Test Result: Failed</em></p>")

            for logstr in self.logdict[tmpkey]:
                report.append("<p>"+logstr.replace("\n", "</br>")+"</p>") 
            report.append("</br>")

        report.append("</body>")
        report.append("</html>")

        x= datetime.now()
        filepath="./output/timesync_report_"+x.strftime("%Y_%B_%d_%H_%M_%S")+".html"

        fo_output = open(filepath, "w")
        fo_output.writelines(report)
        fo_output.close()            

    
    def pushlog(self, temptitle, templog):
        self.logdict[temptitle] =self.logdict[temptitle] + templog
        
    def pushtitle(self, temptitle):
        self.testcnt = self.testcnt+1
        self.logdict[temptitle] = []

    def pushresult(self, temptitle, tempresult):
        self.resultdict[temptitle] = tempresult

    def getSuccessCnt(self):
        return self.successcnt

    def getFailedCnt(self):
        return self.failcnt