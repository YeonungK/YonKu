from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget, QFileDialog
from PyQt5 import uic
import sys
import serial.tools.list_ports

sys.path.append('C:/Users/szkop/Desktop/YonKu')

class SerialInstCreateUi(QWidget):
    def __init__(self):
        super().__init__()
        
        uic.loadUi("GUI/ui_files/serial_instrument_create.ui", self)
        
        """parameters"""
        
        self.name = self.nameLineEdit.text()
        self.model = self.modelLineEdit.text()
        self.interface = 'serial'
        self.description = self.descriptionLineEdit.text()
        self.ports = {}
        self.port = 0
        self.baudrate = self.baudrateLineEdit.text()
        self.bytesize = self.bytesizeComboBox.currentText()
        self.parity = self.parityComboBox.currentText()
        self.stopbits = self.stopbitsComboBox.currentText()
        self.timeout = self.timeoutLineEdit.text()
        self.xonxoff = self.xonxoffLineEdit.text()
        
        self.data_list = {'name':self.name, 'interface':self.interface, 'model':self.model, 'description':self.description, 'port':self.port, 
                          'baudrate':self.baudrate, 'bytesize':self.bytesize, 'parity':self.parity, 'stopbits':self.stopbits, 'timeout':self.timeout, 'xonxoff':self.xonxoff}
        
        """search currently connected ports and add them to the port combo box"""
        
        for port in serial.tools.list_ports.comports():
            self.ports[port.device] = port.description
            self.portComboBox.addItem(port.device)
          
            
        self.descriptionLineEdit.setText(self.ports[self.portComboBox.currentText()])
        self.portComboBox.currentTextChanged.connect(self.change_description)
    
        
        
        
    def change_description(self):
        self.descriptionLineEdit.setText(self.ports[self.portComboBox.currentText()])
    
    def update_parameters(self):
        self.name = self.nameLineEdit.text()
        self.model = self.modelLineEdit.text()
        self.description = self.descriptionLineEdit.text()
        self.port = self.portComboBox.currentText()
        self.baudrate = self.baudrateLineEdit.text()
        self.bytesize = self.bytesizeComboBox.currentText()
        self.parity = self.parityComboBox.currentText()
        self.stopbits = self.stopbitsComboBox.currentText()
        self.timeout = self.timeoutLineEdit.text()
        self.xonxoff = self.xonxoffLineEdit.text()
        
        self.data_list = {'name':self.name, 'interface':self.interface, 'model':self.model, 'description':self.description, 'port':self.port, 
                          'baudrate':self.baudrate, 'bytesize':self.bytesize, 'parity':self.parity, 'stopbits':self.stopbits, 'timeout':self.timeout, 'xonxoff':self.xonxoff}
        
    def device_script(self):
        
        script = f"""#{self.data_list}        

import serial
import time
import sys

sys.path.append('C:/Users/szkop/Desktop/YonKu')

from Tools.Instrument import SerialInstrument


class {self.name}(SerialInstrument):
    def __init__(self, name, port):
        super().__init__(name, '{self.model}', port, baudrate = {self.baudrate}, 
                                bytesize = serial.{self.bytesize}, 
                                parity = serial.{self.parity}, 
                                stopbits = serial.{self.stopbits})
        """
        return script