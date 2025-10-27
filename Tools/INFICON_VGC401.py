import serial
import time

try:
    from Tools.Instrument import SerialInstrument
except:
    from Instrument import SerialInstrument

class pressureGauge(SerialInstrument):
    def __init__(self, name, port:str):
        super().__init__(name, 'inficon_vgc401', port, 
                        baudrate=9600, 
                        bytesize=serial.EIGHTBITS, 
                        parity=serial.PARITY_NONE, 
                        stopbits = serial.STOPBITS_ONE)
    

    def query(self, command:str):
        return self.queryB(command)
    
    def clear(self):
        self.write("*CLS")
        
    def identification(self):
        return self.query("*IDN?")
    
    def pressure_read(self): 
        command = "PR1"
        pressure = self.query(command)
        return pressure
        # try:
        #     pressure = pressure.split()
        #     pressure = pressure[1]
        # except:
        #     return "the pressure gauge is not connected"
        

    def start_record(self):
        pass
    
    def stop_record(self):
        pass
    

if __name__ == "__main__":
    device = pressureGauge('test', 'COM5')

    print(device.pressure_read())
    print(device.pressure_read())
    print(device.pressure_read())
    #for i in range(10):
      #  print(device.read())
      #  device.device.write(b'\x05\n')
      #  time.sleep(0.9)
        
        

    
    device.close()