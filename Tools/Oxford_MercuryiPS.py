import socket
import time

try:
    from Tools.Instrument import EthernetInstrument
except:
    from Instrument import EthernetInstrument



class MagnetPowerSupply(EthernetInstrument):
    def __init__(self, name, ip, port):
        super().__init__(name, 'oxford_mercuryips', ip, port)
        
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
    
    def read_current(self):
        command = 'READ:DEV:MB1.T1:TEMP:SIG:CURR?'
        self.write(command)
        response = self.read()
        return response
    
    def read_temperature(self):
        command = 'READ:DEV:MB1.T1:TEMP:SIG:TEMP?'
        self.write(command)
        response = self.read()
        return response
    
    def read_switch_status(self, axis:str):
        command = 'READ:DEV:GRP' + axis.upper() + ':PSU:SIG:SWHT?'
        self.write(command)
        response = self.read()
        return response
    
    def read_field(self, axis:str):
        command = 'READ:DEV:GRP' + axis.upper() + ':PSU:SIG:FLD?'
        self.write(command)
        response = self.read()
        return response
    
    def read_field_factor(self, axis:str):
        command = 'READ:DEV:GRP' + axis.upper() + ':PSU:ATOB?'
        self.write(command)
        response = self.read()
        return response
    
    def read_target_field(self, axis:str): # axis = 'x', 'y', 'z', 's' 
        command = 'READ:DEV:GRP' + axis.upper() + ':PSU:SIG:FSET?'
        self.write(command)
        response = self.read()
        return response
    
    
#     Hi :) 
    
# if __student__ == "stud"    
#     student = DropOut('model', '???', 'profit')
#     print(student.success())
    
if __name__ == "__main__":
    device = MagnetPowerSupply('test', '192.169.10.100', 7020)
    print(device.read_temperature())