from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget, QFileDialog
from PyQt5 import uic
import sys
import pyvisa

sys.path.append('C:/Users/szkop/Desktop/YonKu')

class GpibInstCreateUi(QWidget):
    def __init__(self):
        super().__init__()
        
        uic.loadUi("GUI/ui_files/gpib_instrument_create.ui", self)
        
        self.rm = pyvisa.ResourceManager()
        self.list = self.rm.list_resources()
        
        
        
        
        for port in self.list:
            gpib_port = port.split("::")
            if gpib_port[0] == 'GPIB0':
                self.addressComboBox.addItem(gpib_port[1])
            else:
                pass
            
        
        """parameters"""
        
        self.name = self.nameLineEdit.text()
        self.interface = 'gpib'
        self.model = self.modelLineEdit.text()
        self.address = self.addressComboBox.currentText()
        
        self.data_list = {'name':self.name, 'interface':self.interface, 'model':self.model, 'address':self.address}
        
        
    def update_parameters(self):
            
        self.name = self.nameLineEdit.text()
        self.interface = 'gpib'
        self.model = self.modelLineEdit.text()
        self.address = self.addressComboBox.currentText()
        
        self.data_list = {'name':self.name, 'interface':self.interface, 'model':self.model, 'address':self.address}

    def device_script(self):
        
        script = f"""#{self.data_list}        

import pyvisa
import time
import sys

sys.path.append('C:/Users/szkop/Desktop/YonKu')

from Tools.Instrument import GPIBInstrument


class {self.name}(GPIBInstrument):
    def __init__(self, name, address):
        super().__init__(name, '{self.model}', address)
        """
        return script
        

if __name__ == "__main__":
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())