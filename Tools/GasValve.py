import nidaqmx
from nidaqmx.constants import LineGrouping

try:
    from Tools.Instrument import NidaqmxInstrument

except:
    from Instrument import NidaqmxInstrument


class gasValve(NidaqmxInstrument):
    def __init__(self, name, device_number, port, range):
        super().__init__(name, 'nidaqmx_usb6525', device_number, port, range)

        self.data = [False, False, False]
        
        if self.connected:
            self.turn_off_all()
        
        
        
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
    
    device.turn_off_SV1()
    device.turn_off_SV2()
    device.turn_off_SV3()
    
    device.close()