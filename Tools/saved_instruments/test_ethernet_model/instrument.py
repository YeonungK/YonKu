
import socket
import time
import sys

from project_paths import PROJECT_ROOT

from Tools.Instrument import EthernetInstrument
from . import attributes


class test_ethernet(EthernetInstrument):
    def __init__(self, name, ip, port):
        super().__init__(name, 'test_ethernet_model', ip, port)
        
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
        
