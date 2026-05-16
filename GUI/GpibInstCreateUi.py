from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget, QFileDialog
from PyQt5 import uic
import sys
import pyvisa

from project_paths import GUI_DIR

class GpibInstCreateUi(QWidget):
    def __init__(self):
        super().__init__()
        
        uic.loadUi(f"{GUI_DIR}/ui_files/gpib_instrument_create.ui", self)
        
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
        
        script = f"""
import pyvisa
import time
import sys

from project_paths import PROJECT_ROOT

from Tools.Instrument import GPIBInstrument
from . import attributes


class {self.name}(GPIBInstrument):
    def __init__(self, name, address):
        super().__init__(name, '{self.model}', address)
        
        self.data_type = attributes.data_type
        self.data_label = attributes.data_label
        self.data_unit = attributes.data_unit
        self.data_function = attributes.data_functions
        self.read_functions = attributes.read_functions
        self.write_functions = attributes.write_functions
        self.initial_state = attributes.initial_state
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

from project_paths import PROJECT_ROOT

from GUI.instrument_control_widgets import base_dynamic_widget

class test_instrument_widget(base_dynamic_widget.widget):
    def __init__(self, instrument):
        super().__init__(instrument, f"GUI/ui_files/instrument_control_uis/{self.model}_ui.ui")
        """
        return script
        

if __name__ == "__main__":
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())