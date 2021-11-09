
#Location:'C:\Users\付君强\Desktop\Work\02_Python'
#Author:Bruce Fu
#Date:2021-10-20
#change log


import os

def hextochar(response):
    #alist = list(response)
    alist_temp = []
    length = len(response)
    length_temp = length//2
    i=0
    while i<length_temp:
        alist_temp.append(response[2*i]+response[2*i+1])
        print(chr(int(alist_temp[i], base=16)), end='')
        i += 1
def main():
    hextochar(Int_response)

if __name__=='__main__':
    Int_response = list(input('please input response:'))
    # hextochar(Int_response)
    main()