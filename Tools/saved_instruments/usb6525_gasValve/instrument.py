#{'name': 'gasValve', 'interface': 'usb6525', 'model': 'usb6525_gasValve', 'deviceNumber': '1', 'port': '0', 'range1': '0', 'range2': '2'}        

import nidaqmx
from nidaqmx.constants import LineGrouping
import sys

sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')

from Tools.Instrument import NidaqmxInstrument


class gasValve(NidaqmxInstrument):
    def __init__(self, name, device_number, port, range):
        super().__init__(name, 'usb6525_gasValve', device_number, port, range)
        
        self.data = [False, False, False]
        self.data_type = {}
        self.data_unit = {}
        self.data_function = {}
        self.initial_state = self.read()
        
        # if self.connected:
        #     self.turn_off_all()
        
    def turn_on_SV1(self):
        self.data[0] = True
        self.write(self.data)
        
    def turn_on_SV2(self):
        self.data[1] = True
        self.write(self.data)
        
    def turn_on_SV3(self):
        self.data[2] = True
        self.write(self.data)
        
    def turn_off_SV1(self):
        self.data[0] = False
        self.write(self.data)
    
    def turn_off_SV2(self):
        self.data[1] = False
        self.write(self.data)
    
    def turn_off_SV3(self):
        self.data[2] = False
        self.write(self.data)
        
    def turn_off_all(self):
        self.data = [False, False, False]
        self.write(self.data)
        
    def turn_on_all(self):
        self.data = [True, True, True]
        self.write(self.data)
        

if __name__ == "__main__":
    device = gasValve("gasValve", "Dev1", "port0", "line0:2")
    
    
    print(device.read())
    
    device.close()