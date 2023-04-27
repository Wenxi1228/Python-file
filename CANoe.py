from distutils.command.build import build
import msvcrt
import os, time, datetime
#from pickle import FALSE
#from numpy import sign
from win32com.client import *
from win32com.client.connect import *
from ping3 import ping
from private.ssh_client import *
import someip
import socket




def DoEvents():
    pythoncom.PumpWaitingMessages()
    time.sleep(0.1)
    
def DoEventsUntil(cond):
    while not cond():
        DoEvents()
        
###Vector CANoe Class
class CANoe:
    Started = False
    Stopped = False
    cfgPath = ""
    def __init__(self):
        self.application = None
        self.application = DispatchEx("CANoe.Application")
        self.application.Configuration.Modified = False
        ver = self.application.Version
        print('Loaded CANoe version: ',
              ver.major, '.',
              ver.minor, '.',
              ver.Build, '...', sep='')
        self.Measurement = self.application.Measurement  
        self.Running = lambda: self.Measurement.Running
        self.WaitForStart = lambda: DoEventsUntil(lambda: CANoe.Started)
        self.WaitForStop = lambda: DoEventsUntil(lambda: CANoe.Stopped)
        WithEvents(self.application.Measurement, CanoeMeasurementEvents)
        
    def loadCfg(self, cfgPath):
        #cfg = os.path.join(os.curdir, cfgPath)
        #cfg = os.path.abspath(cfgPath)
        print('Opening: ', cfgPath)
        self.ConfigPath = os.path.dirname(cfgPath)
        self.Configuration = self.application.Configuration
        self.application.Open(cfgPath)
        
    def closeCfg(self):
        if(self.application != None):
            print("Close cfg ...")
            self.application.Quit()
            self.application = None
    
    def loadTestSetup(self, testsetupPath):
        self.TestSetup = self.application.Configuration.TestSetup
        #self.TestSetup.TestEnvironments.Remove(8, FALSE)
        #path = os.path.join(self.ConfigPath, testsetup)
        #print(path)
        testenv = self.TestSetup.TestEnvironments.Add(testsetupPath)
        testenv = CastTo(testenv, "ITestEnvironment2")
         # TestModules property to access the test modules
        self.TestModules = []
        self.TraverseTestItem(testenv, lambda tm: self.TestModules.append(CanoeTestModule(tm)))
    
    def loadTestConfiguration(self, testcfgname, testunits):
        """ Adds a test configuration and initialize it with a list of existing test units """
        tc = self.application.Configuration.TestConfigurations.Add()
        tc.Name = testcfgname
        tus = CastTo(tc.TestUnits, "ITestUnits2")
        for tu in testunits:
            tus.Add(tu)
        # TestConfigs property to access the test configuration
        self.TestConfigs = [CanoeTestConfiguration(tc)]
            
    def startMeasurement(self):
        if not self.Running():
            self.Measurement.Start()
            self.WaitForStart()

    def stopMeasurement(self):
        if self.Running():
            self.Measurement.Stop()
            self.WaitForStop()
    
    def runTestModules(self):
        """ starts all test modules and waits for all of them to finish"""
        # start all test modules
        for tm in self.TestModules:
            tm.Start()
    
        # wait for test modules to stop
        while not all([not tm.Enabled or tm.IsDone() for tm in app.TestModules]):
            DoEvents()

    def runTestConfigs(self):
        """ starts all test configurations and waits for all of them to finish"""
        # start all test configurations
        for tc in self.TestConfigs:
            tc.Start()
    
        # wait for test modules to stop
        while not all([not tc.Enabled or tc.IsDone() for tc in app.TestConfigs]):
            DoEvents()

    def traverseTestItem(self, parent, testf):
        for test in parent.TestModules: 
            testf(test)
        for folder in parent.Folders: 
            found = self.TraverseTestItem(folder, testf)        
    
        
    def getSigVlu(self, chnlNum, msgName, sigName, busType = 'CAN'):
        if(self.application != None):
            rslt = self.application.GetBus(busType).GetSignal(chnlNum, msgName, sigName)
            return rslt.Value
        else:
            raise RuntimeError("CANoe is not open, unable to get signal Value")
        
    def setSigVlu(self, chnlNum, msgName, sigName, busType, setVlu):
        if(self.application != None):
            rslt = self.application.SetBus(busType).SetSignal(chnlNum, msgName, sigName)
            rslt.Value = setVlu
        else:
            raise RuntimeError("CANoe is not open, unable to set signal value")
        
    def getSysVar(self, ns_name, sysvar_name):
        if(self.application != None):
            systemCAN = self.application.System.Namespaces
            sys_namespace = systemCAN(ns_name)
            sys_value = sys_namespace.Variables(sysvar_name)
            return sys_value.Value
        else:
            raise RuntimeError("CANoe is not open, unable to set signal value")
    
    def setSysVar(self, ns_name, sysvar_name, vlu):
        if(self.application != None):
            systemCAN = self.application.System.Namespaces
            sys_namespace = systemCAN(ns_name)
            sys_value = sys_namespace.Variables(sysvar_name)
            sys_value.Value = vlu
        else:
            raise RuntimeError("CANoe is not open, unable to set signal value")                
        
        
    def TraverseTestItem(self, parent, testf):
        for test in parent.TestModules: 
            testf(test)
        for folder in parent.Folders: 
            found = self.TraverseTestItem(folder, testf)                       

class CanoeMeasurementEvents(object):
    """Handler for CANoe measurement events"""
    def OnStart(self): 
        CANoe.Started = True
        CANoe.Stopped = False
        print("< measurement started >")
    def OnStop(self) : 
        CANoe.Started = False
        CANoe.Stopped = True
        print("< measurement stopped >")

class CanoeTestModule:
    """Wrapper class for CANoe TestModule object"""
    def __init__(self, tm):
        self.tm = tm
        self.Events = DispatchWithEvents(tm, CanoeTestEvents)
        self.Name = tm.Name
        self.IsDone = lambda: self.Events.stopped
        self.Enabled = tm.Enabled
    def Start(self):
        if self.tm.Enabled:
            self.tm.Start()
            self.Events.WaitForStart()

class CanoeTestConfiguration:
    """Wrapper class for a CANoe Test Configuration object"""
    def __init__(self, tc):        
        self.tc = tc
        self.Name = tc.Name
        self.Events = DispatchWithEvents(tc, CanoeTestEvents)
        self.IsDone = lambda: self.Events.stopped
        self.Enabled = tc.Enabled
    def Start(self):
        if self.tc.Enabled:
            self.tc.Start()
            self.Events.WaitForStart()

class CanoeTestEvents:
    """Utility class to handle the test events"""
    def __init__(self):
        self.started = False
        self.stopped = False
        self.WaitForStart = lambda: DoEventsUntil(lambda: self.started)
        self.WaitForStop = lambda: DoEventsUntil(lambda: self.stopped)
    def OnStart(self):
        self.started = True
        self.stopped = False        
        print("<", self.Name, " started >")
    def OnStop(self, reason):
        self.started = False
        self.stopped = True 
        print("<", self.Name, " stopped >")
        

cnt = 0  
preState = ""  
                  
app = CANoe()

app.loadCfg(r"D:\0_Project\3_SAIC_HADS\12_SimuTestCfg\AS33_IECU_CANoe\IECU.cfg")

#app.loadTestSetup(r"C:\Users\jummy\Desktop\AS33_IECU_CANoe\TestEnvironment.tse")

app.startMeasurement()

#app.runTestModules()
app.setSysVar("PythonInterface", "value", 0xFF)


while True:
    if app.getSysVar("PythonInterface", "event") == "wakeup":
        #if preState == "preSleep":
            #sshClient_j3A = ssh_client("192.168.2.10", 5)
            #rslt = sshClient_j3A.sendcmd('date', 1, 256 )
            #print(rslt)
        #app.setSysVar("PythonInterface", "event", "sleep")
        time.sleep(1)
        #print("start PING")
        # 简单用法 ping地址即可，超时会返回None 否则返回耗时，单位默认是秒
        #result_mcu = ping(src_addr = '192.168.2.250', dest_addr = '192.168.2.50', timeout = 1)
        result_mcu = True
        result_j3a = ping(src_addr = '172.31.3.99', dest_addr = '172.31.3.37', timeout = 1)
        #result_j3b = ping(src_addr = '192.168.2.250', dest_addr = '192.168.2.11', timeout = 1)
        result_j3b = True
        result_j3c = ping(src_addr = '172.31.3.99', dest_addr = '172.31.3.67', timeout = 1)
        #print('{}\n    Ping MCU result {}'.format(datetime.datetime.now(), result_mcu))
        print(datetime.datetime.now())
        print('    Ping J3A result {}'.format(result_j3a))
        #print('    Ping J3B result {}'.format(result_j3b))
        print('    Ping J3C result {}\n'.format(result_j3c))
        
        #sshClient_j3A = ssh_client("192.168.2.10", None)
        #rslt = sshClient_j3A.sendcmd('date', 1, 256 )
        #print(rslt)
        if result_mcu is None or result_j3a is None or result_j3b is None or result_j3c is None:
            cnt -= 1
            #print('Ping FAIL {}'.format(result_mcu, result_j3a, result_j3b, result_j3c))
            #print('ping 失败！')
        else:
            #print('Ping OK, response time:{}s'.format(result))
            cnt += 1
            if cnt > 5:
                app.setSysVar("PythonInterface", "pingRslt", 1)
    else:
        cnt = 0
        #if preState == "wakeup":  
            #sshClient_j3A.close()  
    preState = app.getSysVar("PythonInterface", "event")   
    if app.getSysVar("PythonInterface", "event") == "finish":
        break
#app.stopMeasurement()
#app.closeCfg()

#print("Press any key to exit ...")
#while not msvcrt.kbhit():
#    DoEvents()