#{'name': 'temperatureController', 'interface': 'serial', 'model': 'Lakeshore_336', 'description': 'Lake Shore Model 336 Temperature Controller (COM4)', 'port': 'COM4', 'baudrate': '57600', 'bytesize': 'SEVENBITS', 'parity': 'PARITY_ODD', 'stopbits': 'STOPBITS_ONE', 'timeout': '', 'xonxoff': ''}        

import serial
import time
import sys

sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')

from Tools.Instrument import SerialInstrument


class temperatureController(SerialInstrument):
    def __init__(self, name, port):
        super().__init__(name, 'Lakeshore_336', port, baudrate = 57600, 
                                bytesize = serial.SEVENBITS, 
                                parity = serial.PARITY_ODD, 
                                stopbits = serial.STOPBITS_ONE)
        
        self.data_type = {'temperature':['ch_A', 'ch_B', 'ch_C', 'ch_D'], 
                          'resistance': ['ch_A', 'ch_B', 'ch_C', 'ch_D']}
        self.data_unit = {'temperature':'K', 'resistance':'Ohms'}
        self.data_function = {'temperature':self.temp_read_all, 'resistance':self.resist_read_all}
        
    def clear(self):
        self.write("*CLS")
        
    def identification(self):
        return self.query("*IDN?")
    
    def temp_read(self, channel:str): # channel 'A' - 'D'
        command = "KRDG? " + channel
        temp = self.query(command)
        print(temp)
        temp = temp.replace("+","")
        temp = temp.replace("\r","")
        temp = temp.replace("\n","")
        
        temp = float(temp)
        return temp
    
    def temp_read_all(self):
        command = "KRDG? A;KRDG? B;KRDG? C;KRDG? D"
        temp = self.query(command)
        temp = temp.replace("+","")
        temp = temp.replace("\r","")
        temp = temp.replace("\n","")
        temp = temp.split(";")
        i = 0
        while i < len(temp):
            temp[i] = float(temp[i])
            i += 1
        print(temp)
        return temp
    
    def resist_read(self, channel:str): # channel 'A' - 'D'
        command = "SRDG? " + channel
        resistance = self.query(command)
        print(resistance)
        resistance = resistance.replace("+","")
        resistance = resistance.replace("\r","")
        resistance = resistance.replace("\n","")
        
        resistance = float(resistance)
        return resistance
    
    def resist_read_all(self):
        command = "SRDG? A;SRDG? B;SRDG? C;SRDG? D"
        resistance = self.query(command)
        resistance = resistance.replace("+","")
        resistance = resistance.replace("\r","")
        resistance = resistance.replace("\n","")
        resistance = resistance.split(";")
        i = 0
        while i < len(resistance):
            resistance[i] = float(resistance[i])
            i += 1
        print(resistance)
        return resistance

if __name__ == "__main__":
    device = temperatureController('test', 'COM4')
    count = 0
    while count < 5:
        temp = device.resist_read_all()
        count += 1
        time.sleep(0.8)
    device.close()
    
        


















