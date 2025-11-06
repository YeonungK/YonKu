#{'name': 'test', 'interface': 'usb6525', 'model': 'TEST', 'deviceNumber': '1', 'port': '0', 'range1': '0', 'range2': '1'}        

import nidaqmx
from nidaqmx.constants import LineGrouping
import sys

sys.path.append('C:/Users/szkop/Desktop/YonKu')

from Tools.Instrument import NidaqmxInstrument


class test(NidaqmxInstrument):
    def __init__(self, name, device_number, port, range):
        super().__init__(name, 'TEST', device_number, port, range)
        