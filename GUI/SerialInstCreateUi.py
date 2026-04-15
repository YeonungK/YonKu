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
        
        if self.baudrateLineEdit.text() == "":
            self.baudrate = "9600"
        else:
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
                                
        self.data_type = {{}}
        self.data_unit = {{}}
        self.data_function = {{}}
        """
        return script

    def device_ui_script(self):
        
        script = f"""<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>Form</class>
 <widget class="QWidget" name="Form">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>656</width>
    <height>497</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>{self.model}</string>
  </property>
 </widget>
 <resources/>
 <connections/>
</ui>
        """
        return script
    
    def device_wid_script(self):
        
        script = f"""import sys

sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')

from GUI.instrument_control_widgets import base_dynamic_widget

class test_instrument_widget(base_dynamic_widget.widget):
    def __init__(self, instrument):
        super().__init__(instrument, 'GUI/ui_files/instrument_control_uis/{self.model}_ui.ui')
    
        """
        return script