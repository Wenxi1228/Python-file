from scapy.all import *
from scapy.layers.inet import ICMP, IP
from scapy.layers.l2 import Dot1Q, Ether

packet = Ether(dst="02:80:5e:1f:01:25") / \
Dot1Q(vlan=3) / \
IP(dst="172.31.3.37") / \
ICMP() 
sendp(packet)
