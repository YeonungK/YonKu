#{'name': 'pressureGauge', 'interface': 'serial', 'model': 'INFICON_VGC401', 'description': 'Prolific USB-to-Serial Comm Port (COM5)', 'port': 'COM5', 'baudrate': '9600', 'bytesize': 'EIGHTBITS', 'parity': 'PARITY_NONE', 'stopbits': 'STOPBITS_ONE', 'timeout': '', 'xonxoff': ''}        

import serial
import time
import sys

sys.path.append('C:/Users/szkop/Desktop/YonKu')

from Tools.Instrument import SerialInstrument


class pressureGauge(SerialInstrument):
    def __init__(self, name, port):
        super().__init__(name, 'INFICON_VGC401', port, baudrate = 9600, 
                                bytesize = serial.EIGHTBITS, 
                                parity = serial.PARITY_NONE, 
                                stopbits = serial.STOPBITS_ONE)
        
        self.connected = self.check_connection()
        self.data_type = {'pressure':['ch_A']}
        self.data_unit = {'pressure':'mBar'}
        self.data_function = {'pressure': self.pressure_read}
        
    def check_connection(self):
        try:
            self.write("TID")
            time.sleep(1)
            ack=self.read()
            self.device.write(b'\x05\n')
            time.sleep(1)
            idn = self.read()
            idn = idn.split()[0]
            print(idn)
            if idn == "PCG":
                return True
            else:
                return False
        except AttributeError:
            print("AttributeError")
            return False
        
    def query(self, command:str):
        return self.queryB(command)
    
    def clear(self):
        self.write("*CLS")
        
    def identification(self):
        return self.query("*IDN?")
    
    def pressure_read_start(self): #unused
        command = "COM,1"
        pressure = self.query(command)
        try:
            pressure = pressure.split()
            pressure = pressure[1]
            pressure = float(pressure)
            pressure = str(pressure)
            return pressure
        except AttributeError as e:
            print(e)
            msg = "Device Not Connected"
            return msg
        except ValueError:
            msg = "Communication Error"
            return msg
        except IndexError:
            msg = "still connecting"
            return msg
    
    def pressure_read(self):
        command = "PR1"
        pressure = self.query(command)
        
        #pressure = self.read()
        try:
            pressure = pressure.split()
            pressure = pressure[1]
            pressure = float(pressure)
            pressure = str(pressure)
            return pressure
        except AttributeError as e:
            print(e)
            msg = "Device Not Connected"
            return msg
        except ValueError:
            msg = "Communication Error"
            return msg
        except IndexError:
            msg = "still connecting"
            return msg
        
        
        

    

if __name__ == "__main__":
    device = pressureGauge('test', 'COM5')
    print(device.check_connection())
    device.pressure_read_start()
    for i in range(30):
        print(device.pressure_read())
        time.sleep(1)
    
    device.close()
        