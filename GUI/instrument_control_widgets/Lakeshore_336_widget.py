from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget
from PyQt5 import uic
import sys


from project_paths import INSTRUMENT_CONTROL_UIS_DIR

from GUI import ChsBigLineUi as chs


class temperatureController_widget(QWidget):
    def __init__(self, instrument, device_info, device_key, parent):
        super().__init__()
        
        self.instrument = instrument
        self.data_list = device_info
        self.device_key = device_key
        self.parent = parent
        uic.loadUi(f"{INSTRUMENT_CONTROL_UIS_DIR}/Lakeshore_336_ui.ui", self)
        
        self.chA_line_sub = chs.chABigLineUi()
        self.chA_line_sub.hide()
        
        self.chB_line_sub = chs.chBBigLineUi()
        self.chB_line_sub.hide()
        
        self.chC_line_sub = chs.chCBigLineUi()
        self.chC_line_sub.hide()
        
        self.chD_line_sub = chs.chDBigLineUi()
        self.chD_line_sub.hide()
        
        
        
        
        
     # [---------temperature controller ui output signals---------]
     
        self.unitSwitchButton.clicked.connect(self.switch_unit)
        
        self.chAExpandButton.clicked.connect(self.expand_chA_line)
        self.chBExpandButton.clicked.connect(self.expand_chB_line)
        self.chCExpandButton.clicked.connect(self.expand_chC_line)
        self.chDExpandButton.clicked.connect(self.expand_chD_line) # [/]
    
    
    # [...........functions...........]
    
    def initialize_widget(self):
        pass
        
    def expand_chA_line(self):
        self.chA_line_sub.show()
        
    def expand_chB_line(self):
        self.chB_line_sub.show()
    
    def expand_chC_line(self):
        self.chC_line_sub.show()
    
    def expand_chD_line(self):
        self.chD_line_sub.show()
    
    def switch_unit(self):
        if self.unitSwitchButton.isChecked():
            self.unitSwitchButton.setText("Current Unit: Temperature (K)")
        else:
            self.unitSwitchButton.setText("Current Unit: Resistance (Ohms)")
    
      # [/]
   
        