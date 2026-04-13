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
        
        
        
        self.pumpPushButton.toggled.connect(self.change_state)
        self.ivcPushButton.toggled.connect(self.change_state)
        self.hePushButton.toggled.connect(self.change_state)
        
        self.allOffPushButton.clicked.connect(self.off_state)
        self.allOnPushButton.clicked.connect(self.on_state)
    
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