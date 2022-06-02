from numpy import float32, uint8, uint16, uint32

a=-10.001
b= uint8(a)
c= uint16(a*2.0+34)
d= uint32(c)
print(a,type(a),b,type(b),c,type(c),d,type(d))

#