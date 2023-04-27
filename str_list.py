import sys
import csv
result=[]
j = 0
with open('vin.txt',mode = 'r') as f:
	for i in f:
		while j < (len(i)):
			print(len(i))
			print(int(i[j: j+4], 16),type(int(i[j: j+4], 16)))

			result.append(int(i[j: j+4], 16))
			j += 5
print(type(result),len(result))
send_list=[0x02, 0xfd, 0x00, 0x03]+[0]*3+[0x11]+result
print(send_list)

mcu_version = '02.66.88.xx'
print(mcu_version[:8])
	#print(list(result))

