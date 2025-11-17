import pyvisa
import serial
import socket
import time
import nidaqmx
from nidaqmx.constants import LineGrouping


class ScientificInstrument:
    def __init__(self, name, model, interface):
        self.interface = interface
        self.name = name
        self.model = model
        
    def connect(self):
        pass
    
    def read(self):
        pass
    
    def write(self):
        pass
    
    def query(self):
        pass
    
    def close(self):
        pass
    
class EthernetInstrument(ScientificInstrument):
    def __init__(self, name, model, ip, port):
        super().__init__(name, model, 'ethernet')
        self.ip = ip
        self.port = port
        self.connected = False
        self.device = self.connect()
    
    def connect(self):
        device = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            device.connect((self.ip, self.port))
            print(f'connected: {self.model}.{self.name}')
            self.connected = True
            return device
        except socket.error:
            print(f"connection failure: {self.model}.{self.name}, this ethernet ip or port doesn't exist")
            return None
        
    
    def read(self):
        try: 
            response = self.device.recv(1024).decode('ascii')
            return response
        except socket.error:
            print(f"There is no response. {socket.error}")
            return None
        except:
            print('There is no resposne.')
            return None
       
    
    def write(self, command:str):
        command += "\n"
        try:
            self.device.sendall(command.encode('ascii'))
        except socket.error:
            print(f"There is no response. {socket.error}")
        except:
            print('There is no resposne.')
    
class SerialInstrument(ScientificInstrument):
    def __init__(self, name, model, port:str, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE):
        super().__init__(name, model, 'serial')
        self.port = port           # for example: 'COM4'
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.connected = False
        self.device = self.connect()
        
        
    def connect(self):
        
        try:
            device = serial.Serial(self.port, self.baudrate, self.bytesize, self.parity, self.stopbits)
            print(f'connected: {self.model}.{self.name}')
            self.connected = True
            return device
        except serial.SerialException:
            print(f'connection failure: {self.model}.{self.name}, this port does not exist')
            return None
        
        
    
    def read(self):
        response = None
        if self.device.in_waiting > 0:
            response = self.device.readline().decode('ascii')
        else: print("There is no response.")
        time.sleep(0.1)
        return response
    
    def write(self, command:str):
        message = command + "\n"
        self.device.write(message.encode('ascii'))
        time.sleep(0.1)
        
    def query(self, command:str):
        self.write(command)
        response = self.read()
        return response
    
    def queryB(self, command:str):
        self.write(command)
        time.sleep(0.5)
        response1 = self.read()
        
        self.device.write(b'\x05\n')
        time.sleep(0.5)
        response2 = self.read()
        print(response2)
        return response2
    
    def close(self):
        self.device.close()

class GPIBInstrument(ScientificInstrument):
    def __init__(self, name, model, address):
        super().__init__(name, model, 'gpib')
        self.address = address
        self.rm = pyvisa.ResourceManager()
        self.address = 'GPIB0::' + str(address) + '::INSTR'
        self.connected = False
        self.device = self.connect()
        

        
    def connect(self):
        device = None
        device_list = self.rm.list_resources()
        # print(device_list)
        if self.address in device_list:
            device = self.rm.open_resource(self.address)
            print(f"connected: {self.model}.{self.name}")
            self.connected = True
        else: 
            print(f"connection failure: {self.model}.{self.name}, this gpib address does not exist.")
        return device
    
    def read(self):
        pass
    
    def write(self, command:str):
        self.device.write(command)
        time.sleep(0.1)
    
    def query(self, command:str):
        response = self.device.query(command)
        time.sleep(0.1)
        return response
    
    def close(self):
        self.device.close()
        
class NidaqmxInstrument(ScientificInstrument):
    def __init__(self, name, model, device_number, port, range):  # device_number: Dev#,  port: port#, range: line#:#
        super().__init__(name, model, 'nidaqmx')
        self.device_number = device_number
        self.port = port
        self.range = range
        self.connected = False
        self.device = self.connect()
        
        
        
        
    def connect(self):
        try:
            task = nidaqmx.Task()
            address = self.device_number + "/" + self.port + "/" + self.range
            task.do_channels.add_do_chan(address, line_grouping=LineGrouping.CHAN_PER_LINE)
            print(f'connected: {self.model}.{self.name}')
            self.connected = True
            return task
        except:
            print(f'connection failure: {self.model}.{self.name}')
            return None
    
    def read(self):
        pass
    
    def write(self, data): # data: a list of boolean for each pin
        self.device.write(data)
        
    
    def query(self):
        pass
    
    def close(self):
        self.device.close()
        
if __name__ == "__main__":
    
    """336 temperature controller test"""
    tempController = SerialInstrument('Lakeshore 336 Temp Controller', 'COM4', 
                                      baudrate = 57600, 
                                      bytesize = serial.SEVENBITS, 
                                      parity=serial.PARITY_ODD, 
                                      stopbits = serial.STOPBITS_ONE)
    response = tempController.query("*IDN?")
    print(response)
    tempController.close()
    
    
    """pressure gauge test"""
    # pressureGauge = SerialInstrument('INFICON Pressure Gauge', 'COM5', 
    #                                   baudrate=9600, 
    #                                   bytesize=serial.EIGHTBITS, 
    #                                   parity=serial.PARITY_NONE, 
    #                                   stopbits = serial.STOPBITS_ONE)
    
    # response = pressureGauge.queryB("PR1")
    # print(response)
    # pressureGauge.close()
    
    """gas valve test"""
    # gasValve = NidaqmxInstrument('Gas Valve', "Dev1", "port0", "line0:2")
    # data = [False, False, False]
    # gasValve.write(data)
    # gasValve.close()
    
    """SR830 Lock in Amp test"""
    # lockInAmplifier = GPIBInstrument('SR830 Lock In Amplifier', 8)
    # response = lockInAmplifier.query("*IDN?")
    # print(response)
    # lockInAmplifier.close()