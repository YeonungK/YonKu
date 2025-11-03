#{'name': 'test', 'interface': 'serial', 'model': 'TEST', 'description': 'Intel(R) Active Management Technology - SOL (COM3)', 'port': 'COM3', 'baudrate': '9600', 'bytesize': 'FIVEBITS', 'parity': 'PARITY_NONE', 'stopbits': 'STOPBITS_ONE', 'timeout': '', 'xonxoff': ''}        

import serial
import time
import sys

sys.path.append('C:/Users/szkop/Desktop/YonKu')

from Tools.Instrument import SerialInstrument


class test(SerialInstrument):
    def __init__(self, name, port):
        super().__init__(name, 'TEST', port, baudrate = 9600, 
                                bytesize = serial.FIVEBITS, 
                                parity = serial.PARITY_NONE, 
                                stopbits = serial.STOPBITS_ONE)
        