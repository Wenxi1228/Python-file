import scapy
from scapy.all import *
from scapy.utils import PcapReader

def deltatcheck(Port,file):
  packets = rdpcap(file)
  count=0
  time1=0
  for data in packets:
    if 'UDP' in data:
      if data.dport==Port:
        count=count+1
        time2=data.time
        deltat=time2-time1
        #list=list.append(Port)
        #print(Port,count, deltat)
        if deltat>0.011 or deltat<0.009:   #1ms tolerance 10%
          if count>1:
            print('Port=',Port,'cycle time is wrong')
            print(Port, count, deltat)
            #break;
        time1=time2
      else:
        pass
    else:
      pass
  print('Port=',Port,'共有包:',count,'cycle time is correct')


if __name__ =="__main__":
  file="./Proto.pcapng"
  Port1=15001
  Port2=15002
  list1=[]
  list2=[]
  deltatcheck(Port1,file)
  deltatcheck(Port2,file)


"""
  if 'UDP' in data:
    s = repr(data)
    print(s)
    print(data['UDP'].sport)
    break
"""
