#{'name': 'magnetPowerSupply', 'interface': 'ethernet', 'model': 'Oxford_MercuryiPS', 'instIP': '192.169.10.100', 'port': '7020'}        

import socket
import time
import sys

sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')

from Tools.Instrument import EthernetInstrument


class magnetPowerSupply(EthernetInstrument):
    def __init__(self, name, ip, port):
        super().__init__(name, 'Oxford_MercuryiPS', ip, port)
        self.data_type = {'field':['field'], 'current':['current']}
        self.data_unit = {'field':'T', 'current':'A'}
        self.data_function = {'field':self.read_all_field, 'current': self.read_current}
    
    
    
    
    def identification(self):
        self.write("*IDN?")
        response = self.read()
        return response
    
    def device_list(self):
        self.write("READ:SYS:CAT?")
        response = self.read()
        return response
    
    def set_mode(self, mode:str, password:str):  # mode = either 'ENG' or 'NORM'
        if mode == 'ENG':
            command = 'SET:SYS:MODE:ENG:PASS:' + password
        elif mode == 'NORM':
            command = 'SET:SYS:MODE:NORM'
        else:
            print("Invalid mode input")
            return None
        self.write(command)
        response = self.read()
        return response
    
    def set_current_lim(self, axis:str, value:float): # axis = 'x', 'y', 'z', 's'  /  value = float (0.0 to 360.00)
        command = 'SET:DEV:GRP' + axis.upper() + ':PSU:SIG:CLIM:' + str(value)
        self.write(command)
        response = self.read()
        return response
        
    def read_current_lim(self, axis:str): # axis = 'x', 'y', 'z', 's'  /  value = float (0.0 to 360.00)
        command = 'READ:DEV:GRP' + axis.upper() + ':PSU:SIG:CLIM?'
        self.write(command)
        response = self.read()
        return response
    
    def set_target_field(self, axis:str, value:float): # axis = 'x', 'y', 'z', 's'  /  value = float (-CLIM/ATOB to CLIM/ATOB)
        command = 'SET:DEV:GRP' + axis.upper() + ':PSU:SIG:FSET:' + str(value)
        self.write(command)
        response = self.read()
        return response
        
    def set_field_rate(self, axis:str, value:float): # axis = 'x', 'y', 'z', 's'  /  value = float (0 to 50)
        command = 'SET:DEV:GRP' + axis.upper() + ':PSU:SIG:RFST:' + str(value)
        self.write(command)
        response = self.read()
        return response
    
    def read_field_rate(self, axis:str): # axis = 'x', 'y', 'z', 's' 
        command = 'READ:DEV:GRP' + axis.upper() + ':PSU:SIG:RFST?'
        self.write(command)
        response = self.read()
        response = response.replace('T/m\n', "")
        response = response.split(':')
        response = response[-1]
        return response
    
    def read_current(self):
        try:
            command = 'READ:DEV:MB1.T1:TEMP:SIG:CURR?'
            self.write(command)
            response = self.read()
            response = response.replace('K\n', "")
            response = response.split(':')
            response = response[-1]
            
        except:
            response = 0
        response_list = [response]
        print(response_list)
        return response_list
    
    def read_temperature(self):
        command = 'READ:DEV:MB1.T1:TEMP:SIG:TEMP?'
        self.write(command)
        response = self.read()
        response = response.replace('K\n', "")
        response = response.split(':')
        response = response[-1]
        return response
    
    def read_switch_status(self, axis:str):
        command = 'READ:DEV:GRP' + axis.upper() + ':PSU:SIG:SWHT?'
        self.write(command)
        response = self.read()
        return response
    
    def set_switch_status(self, axis:str, power:str):
        command = 'SET:DEV:GRP' + axis.upper() + f':PSU:SIG:SWHT:{power.upper()}'
        self.write(command)
        response = self.read()
        return response


    def read_all_switch_status(self):
        x = self.read_switch_status('x').replace('\n',"")
        y = self.read_switch_status('y').replace('\n',"")
        z = self.read_switch_status('z').replace('\n',"")
        
        response = {'x': x, 'y': y, 'z': z}
        return response
    
    def read_field(self, axis:str):
        command = 'READ:DEV:GRP' + axis.upper() + ':PSU:SIG:FLD?'
        self.write(command)
        response = self.read()
        return response
    
    def read_all_field(self):
        try:   
            x = float(self.read_field('x').replace('\n',"").split(":")[-1].replace('T',""))
            y = float(self.read_field('y').replace('\n',"").split(":")[-1].replace('T',""))
            z = float(self.read_field('z').replace('\n',"").split(":")[-1].replace('T',""))
            
            response = z
        except:
            response = 0
        response_list = [response]
        print(response_list)
        return response_list
    
    def read_field_factor(self, axis:str):
        command = 'READ:DEV:GRP' + axis.upper() + ':PSU:ATOB?'
        self.write(command)
        response = self.read()
        return response
    
    def read_target_field(self, axis:str): # axis = 'x', 'y', 'z', 's' 
        command = 'READ:DEV:GRP' + axis.upper() + ':PSU:SIG:FSET?'
        self.write(command)
        response = self.read()
        response = response.replace('T\n', "")
        response = response.split(':')
        response = response[-1]
        return response
    
    
if __name__ == "__main__":
    device = magnetPowerSupply('test', '192.169.10.100', 7020)
    print(device.read_all_field())
    print(device.set_switch_status('Z','OFF'))
    