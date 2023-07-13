import os
import time
from contextlib import suppress
import paramiko
from win32com.client import *
from win32com.client.connect import *


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
        # cfg = os.path.join(os.curdir, cfgPath)
        # cfg = os.path.abspath(cfgPath)
        print('Opening: ', cfgPath)
        self.ConfigPath = os.path.dirname(cfgPath)
        self.Configuration = self.application.Configuration
        self.application.Open(cfgPath)

    def closeCfg(self):
        if (self.application != None):
            print("Close cfg ...")
            self.application.Quit()
            self.application = None

    def loadTestSetup(self, testsetupPath):
        self.TestSetup = self.application.Configuration.TestSetup
        # self.TestSetup.TestEnvironments.Remove(8, FALSE)
        # path = os.path.join(self.ConfigPath, testsetup)
        # print(path)
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

    def getSigVlu(self, chnlNum, msgName, sigName, busType='CAN'):
        if (self.application != None):
            rslt = self.application.GetBus(busType).GetSignal(chnlNum, msgName, sigName)
            return rslt.Value
        else:
            raise RuntimeError("CANoe is not open, unable to get signal Value")

    def setSigVlu(self, chnlNum, msgName, sigName, busType, setVlu):
        if (self.application != None):
            rslt = self.application.SetBus(busType).SetSignal(chnlNum, msgName, sigName)
            rslt.Value = setVlu
        else:
            raise RuntimeError("CANoe is not open, unable to set signal value")

    def getSysVar(self, ns_name, sysvar_name):
        if (self.application != None):
            systemCAN = self.application.System.Namespaces
            sys_namespace = systemCAN(ns_name)
            sys_value = sys_namespace.Variables(sysvar_name)
            return sys_value.Value
        else:
            raise RuntimeError("CANoe is not open, unable to set signal value")

    def setSysVar(self, ns_name, sysvar_name, vlu):
        if (self.application != None):
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

    def OnStop(self):
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

def version_read(host_name):
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
    stdin, stdout, stderr = ssh.exec_command("cat /tmp/mcu_version")
    tmp = stdout.read().decode().strip('\n')
    version_result.append(tmp)
    #print(device, version_result)
    print("mcu version is :"+str(version_result))
    return tmp


if __name__=='__main__':
    check_times = 1
    result = []
    app = CANoe()
    record_times = 0
    cnt = 0
    app.loadCfg(r"C:\Users\付君强\Desktop\Work\08_Project\16_J3一体机\12_CANoe\123005_EP32_CANoeEnv_230217\123005_EP32_FLC_Simulate_Env_CANoe14.0_230217.cfg")

    while cnt < 5000:
        if app.getSysVar("PythonIf", "WakeupEvent") == 1 and record_times == 0:
            print(app.getSysVar("PythonIf", "WakeupEvent"))
            print("The", check_times, "timesync test")
            time.sleep(1)
            times="The " + str(check_times) + " timesync test"
            result.append(times)
            J3_result = read_timestamp("172.16.50.12", "J3")
            result.append(J3_result)
            J3_result = version_read("172.16.50.12")
            result.append(J3_result)
            check_times += 1
            record_times = 1
            cnt += 1

        elif app.getSysVar("PythonIf", "WakeupEvent") == 0:
            record_times = 0


    #print(result)
    f = open("D:\Testresult.txt", mode = "w")
    for i in result:
        f.write(i)
        f.write('\r\n')
    f.close()

    

