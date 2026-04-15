from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget, QFileDialog
from PyQt5 import uic
import sys
import socket

sys.path.append('C:/Users/szkop/Desktop/YonKu')

class EthernetInstCreateUi(QWidget):
    def __init__(self):
        super().__init__()
        
        uic.loadUi("GUI/ui_files/ethernet_instrument_create.ui", self)
        
        """parameters"""
        
        self.name = self.nameLineEdit.text()
        self.interface = 'ethernet'
        self.model = self.modelLineEdit.text()
        
        self.hostname = socket.gethostname()
        self.pcIP = socket.gethostbyname(self.hostname)
        
        self.pcIpAddressLineEdit.setText(self.pcIP)
        
        self.instIP = self.instIpAddressLineEdit.text()
        self.port = self.portLineEdit.text()
        
        self.data_list = {'name':self.name, 'interface':self.interface, 'model':self.model, 'instIP':self.instIP, 'port':self.port}
        
    def update_parameters(self):
        
        self.name = self.nameLineEdit.text()
        self.interface = 'ethernet'
        self.model = self.modelLineEdit.text()
        self.instIP = self.instIpAddressLineEdit.text()
        self.port = self.portLineEdit.text()
        
        self.data_list = {'name':self.name, 'interface':self.interface, 'model':self.model, 'instIP':self.instIP, 'port':self.port}
        
    def device_script(self):
        
        script = f"""#{self.data_list}        

import socket
import time
import sys

sys.path.append('C:/Users/szkop/Desktop/YonKu')

from Tools.Instrument import EthernetInstrument


class {self.name}(EthernetInstrument):
    def __init__(self, name, ip, port):
        super().__init__(name, '{self.model}', ip, port)
        
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
        
        script = f"""sys

sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')

from GUI.instrument_control_widgets import base_dynamic_widget

class test_instrument_widget(base_dynamic_widget.widget):
    def __init__(self, instrument):
        super().__init__(instrument, 'GUI/ui_files/instrument_control_uis/{self.model}_ui.ui')
        """
        return script
        
        
if __name__ == "__main__":
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    
    print(ip)
        