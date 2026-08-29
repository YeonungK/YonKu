#{'name': 'pressureGauge', 'interface': 'serial', 'model': 'INFICON_VGC401', 'description': 'Prolific USB-to-Serial Comm Port (COM5)', 'port': 'COM5', 'baudrate': '9600', 'bytesize': 'EIGHTBITS', 'parity': 'PARITY_NONE', 'stopbits': 'STOPBITS_ONE', 'timeout': '', 'xonxoff': ''}        

import serial
import time
import sys

sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')

from Tools.Instrument import SerialInstrument
from . import attributes


class pressureGauge(SerialInstrument):
    def __init__(self, name, port):
        super().__init__(name, 'INFICON_VGC401', port, baudrate = 9600, 
                                bytesize = serial.EIGHTBITS, 
                                parity = serial.PARITY_NONE, 
                                stopbits = serial.STOPBITS_ONE)
        
        self.connected = self.check_connection()
        self.data_type = attributes.data_type
        self.data_label = attributes.data_label
        self.data_unit = attributes.data_unit
        self.value_format = attributes.value_format
        self.data_function = {
            data_type_id: function.__get__(self, type(self))
            for data_type_id, function in attributes.data_functions.items()
        }
        self.read_functions = attributes.read_functions
        self.write_functions = attributes.write_functions
        self.initial_state = attributes.initial_state
        
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
        # print(pressure)
        pressure_list = []
        
        #pressure = self.read()
        try:
            pressure = pressure.split()
            pressure = pressure[1]
            pressure = float(pressure)
            pressure = str(pressure)
            pressure_list.append(pressure)
        except AttributeError as e:
            print(e)
            msg = "Device Not Connected"
            pressure_list.append(msg)
        
        except ValueError:
            msg = "Communication Error"
            pressure_list.append(msg)
        
        except IndexError:
            msg = "still connecting"
            pressure_list.append(msg)
        
        except TypeError:
            msg = "None"
            pressure_list.append(msg)
        
        # print(pressure_list)
        return pressure_list
        
        
        

    

if __name__ == "__main__":
    device = pressureGauge('test', 'COM5')
    print(device.check_connection())
    device.pressure_read_start()
    for i in range(30):
        print(device.pressure_read())
        time.sleep(1)
    
    device.close()
        
