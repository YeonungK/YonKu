
import socket
import time
import sys

from project_paths import PROJECT_ROOT

from Tools.Instrument import EthernetInstrument
from . import attributes


class TestPressureController(EthernetInstrument):
    def __init__(self, name, ip, port):
        super().__init__(name, 'Pseudo_1353', ip, port)
        
        self.data_type = attributes.data_type
        self.data_label = attributes.data_label
        self.data_unit = attributes.data_unit
        self.data_function = attributes.data_functions
        self.read_functions = attributes.read_functions
        self.write_functions = attributes.write_functions
        self.initial_state = attributes.initial_state
        