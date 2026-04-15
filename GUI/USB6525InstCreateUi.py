from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget, QFileDialog
from PyQt5 import uic
import sys
import nidaqmx
from nidaqmx.constants import LineGrouping

sys.path.append('C:/Users/szkop/Desktop/YonKu')

class usb6525InstCreateUi(QWidget):
    def __init__(self):
        super().__init__()
        
        uic.loadUi("GUI/ui_files/usb_6525_create.ui", self)
        
        """parameters"""
        
        self.name = self.nameLineEdit.text()
        self.interface = 'usb6525'
        self.model = self.modelLineEdit.text()
        self.device_number = self.deviceNumberLineEdit.text()
        self.port = self.portLineEdit.text()
        self.range1 = self.range1LineEdit.text()
        self.range2 = self.range2LineEdit.text()

        self.data_list = {'name':self.name, 'interface':self.interface, 'model':self.model, 'deviceNumber':self.device_number, 'port':self.port, 
                          'range1':self.range1, 'range2':self.range2}
        
        
    def update_parameters(self):
        
        self.name = self.nameLineEdit.text()
        self.interface = 'usb6525'
        self.model = self.modelLineEdit.text()
        self.device_number = self.deviceNumberLineEdit.text()
        self.port = self.portLineEdit.text()
        self.range1 = self.range1LineEdit.text()
        self.range2 = self.range2LineEdit.text()

        self.data_list = {'name':self.name, 'interface':self.interface, 'model':self.model, 'deviceNumber':self.device_number, 'port':self.port, 
                          'range1':self.range1, 'range2':self.range2}
        
        
    def device_script(self):
        
        script = f"""#{self.data_list}        

import nidaqmx
from nidaqmx.constants import LineGrouping
import sys

sys.path.append('C:/Users/szkop/Desktop/YonKu')

from Tools.Instrument import NidaqmxInstrument


class {self.name}(NidaqmxInstrument):
    def __init__(self, name, device_number, port, range):
        super().__init__(name, '{self.model}', device_number, port, range)
        
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
    pass

