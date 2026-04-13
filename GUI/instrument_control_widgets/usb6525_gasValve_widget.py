import sys

sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')


from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5 import uic

class gasValve_widget(QWidget):
    def __init__(self, instrument):
        super().__init__()
        
        self.instrument = instrument
        
        uic.loadUi('GUI/ui_files/instrument_control_uis/usb6525_gasValve_ui.ui', self)
        
        self.valves = [self.pumpPushButton, self.ivcPushButton, self.hePushButton]
        self.pumpPushButton.setCheckable(True)
        self.ivcPushButton.setCheckable(True)
        self.hePushButton.setCheckable(True)
        
        for button in self.valves:
            button.setText("CLOSED")
            button.setStyleSheet(
                "background-color: red; color: black"
            )
        
        
    # [----------gas valve and pressure gauge ui signals---------]
        
        self.pumpPushButton.toggled.connect(self.pump_change)
        self.ivcPushButton.toggled.connect(self.ivc_change)
        self.hePushButton.toggled.connect(self.he_change)
        self.allOffPushButton.clicked.connect(self.gas_all_off)
        self.allOnPushButton.clicked.connect(self.gas_all_on)
        self.pumpPushButton.toggled.connect(self.change_state)
        self.ivcPushButton.toggled.connect(self.change_state)
        self.hePushButton.toggled.connect(self.change_state)
        
        self.allOffPushButton.clicked.connect(self.off_state)
        self.allOnPushButton.clicked.connect(self.on_state) # [/]
        
        
 # [...........functions...........]
    
    def pump_change(self):
        if self.pumpPushButton.isChecked():
            self.instrument.turn_on_SV1()
        else:
            self.instrument.turn_off_SV1()
    
    def ivc_change(self):
        if self.ivcPushButton.isChecked():
            self.instrument.turn_on_SV2()
        else:
            self.instrument.turn_off_SV2()
    
    def he_change(self):
        if self.hePushButton.isChecked():
            self.instrument.turn_on_SV3()
        else:
            self.instrument.turn_off_SV3()  
    
    def gas_all_off(self):
        self.instrument.turn_off_all()      
    
    def gas_all_on(self):
        self.instrument.turn_on_all()
    
    def off_state(self):
        for button in self.valves:
            button.setChecked(False)
    
    def on_state(self):
        for button in self.valves:
            button.setChecked(True)
            
    def change_state(self):
        
        for button in self.valves:
            if button.isChecked():
                button.setText("OPEN")
                button.setStyleSheet(
                    "background-color: green; color: black"
                )
            else:
                button.setText("CLOSED")
                button.setStyleSheet(
                    "background-color: red; color: black"
                )
         # [/]
    
        
        
        
    
