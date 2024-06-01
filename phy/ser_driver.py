import serial
from enum import Enum
class Mode(Enum):
    V = 1
    G = 2
    Z = 3
def get_bin(arg):
    if(arg==Mode.V):
        return '10'
    elif(arg==Mode.G):
        return '00'
    else:
        return '01'
class Ser_driver:
    def __init__(self) -> None:
        self.ser=serial.Serial("/dev/ttyAMA0",115200)
        self.head='BC'
        self.mode1='81'
        self.mode2='52'
        self.voltage='7F'
        self.duty='65'
        self.freq='0064'
        self.tail='9999FFDF'
    def set_mode1(self,isreply:bool):
        if(isreply):
            self.mode1='81'
        else:
            self.mode1="01"
        print('mode1 is {}'.format(self.mode1))
    def set_mode2(self,Channel1=Mode.V,Channel2=Mode.V,Channel3=Mode.V,Channel4=Mode.V):
        bin_l=[]
        bin_l.append(get_bin(Channel4))
        bin_l.append(get_bin(Channel3))
        bin_l.append(get_bin(Channel2))
        bin_l.append(get_bin(Channel1))
        bin_string=''.join(bin_l)
        hex_string = hex(int(bin_string, 2))[2:4]
        if len(hex_string) % 2 != 0:
            hex_string = '0' + hex_string
        self.mode2= hex_string
        print('mode2 is {}'.format(self.mode2))
    def set_voltage(self,voltage:str):
        if(len(voltage)==2):
            self.voltage=voltage
        print('voltage is {}'.format(self.voltage))
    def set_duty(self,enable:bool,duty:int):
        i=0
        if(duty>=0 and duty<=100):
            i+=(duty<<1)
        if(enable):
            i+=1
        self.duty='{:02X}'.format(i)
        print('duty is {}'.format(self.duty))
    def set_frequency(self,frequency:int):
        self.freq='{:04X}'.format(frequency)
        print('frequency is {}'.format(self.freq))
    def send(self):
        total=self.head+self.mode1+self.mode2+self.voltage+self.duty+self.freq+self.tail
        self.ser.write(bytes.fromhex(total))

# tmp= 'BC 81 52 00 64 00 64 88 88 FF DF'


# ser.write(bytes.fromhex(tmp))