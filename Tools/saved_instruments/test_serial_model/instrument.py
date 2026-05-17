
import serial
import time
import sys

from project_paths import PROJECT_ROOT

from Tools.Instrument import SerialInstrument
from . import attributes


class test_serial(SerialInstrument):
    def __init__(self, name, port):
        super().__init__(name, 'test_serial_model', port, baudrate = 9600, 
                                bytesize = serial.FIVEBITS, 
                                parity = serial.PARITY_NONE, 
                                stopbits = serial.STOPBITS_ONE)
                                
        self.data_type = attributes.data_type
        self.data_label = attributes.data_label
        self.data_unit = attributes.data_unit
        self.data_function = attributes.data_functions
        self.read_functions = attributes.read_functions
        self.write_functions = attributes.write_functions
        self.initial_state = attributes.initial_state
        