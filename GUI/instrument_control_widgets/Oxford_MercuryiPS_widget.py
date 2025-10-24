import sys
from datetime import datetime
from zoneinfo import ZoneInfo
sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')


from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5 import uic

class magnetPowerSupply_widget(QWidget):
    def __init__(self):
        super().__init__()
        
        uic.loadUi("GUI/ui_files/instrument_control_uis/Oxford_MercuryiPS_ui.ui", self)
        
        self.heaterButtons = [self.switchHeaterXbutton, self.switchHeaterYbutton, self.switchHeaterZbutton]
        self.switchHeaterXbutton.setCheckable(True)
        self.switchHeaterYbutton.setCheckable(True)
        self.switchHeaterZbutton.setCheckable(True)
        
        self.switchHeaterXbutton.toggled.connect(self.switch_x_change_state)
        self.switchHeaterYbutton.toggled.connect(self.switch_y_change_state)
        self.switchHeaterZbutton.toggled.connect(self.switch_z_change_state)
        
    
    def off_state(self, button):
        
        button.setChecked(False)
        button.setText("OFF")
        button.setStyleSheet(
            "background-color: red; color: black"
        )
        
    def on_state(self, button):
        
        button.setChecked(True)
        button.setText("ON")
        button.setStyleSheet(
            "background-color: green; color: black"
        )
        
    def switch_x_change_state(self):
        
        if self.switchHeaterXbutton.isChecked():
            self.switchHeaterXbutton.setText("ON")
            self.switchHeaterXbutton.setStyleSheet(
                "background-color: green; color: black"
            )

        else:
            self.switchHeaterXbutton.setText("OFF")
            self.switchHeaterXbutton.setStyleSheet(
                "background-color: red; color: black"
            )
        
        now = datetime.now()
        now.strftime('%Y-%m-%d %H:%M:%S')
        self.switchHeaterXLineEdit.setText(str(now))
    
    def switch_y_change_state(self):
        
        if self.switchHeaterYbutton.isChecked():
            self.switchHeaterYbutton.setText("ON")
            self.switchHeaterYbutton.setStyleSheet(
                "background-color: green; color: black"
            )

        else:
            self.switchHeaterYbutton.setText("OFF")
            self.switchHeaterYbutton.setStyleSheet(
                "background-color: red; color: black"
            )
        
        now = datetime.now()
        now.strftime('%Y-%m-%d %H:%M:%S')
        self.switchHeaterYLineEdit.setText(str(now))
        
    def switch_z_change_state(self):
        
        if self.switchHeaterZbutton.isChecked():
            self.switchHeaterZbutton.setText("ON")
            self.switchHeaterZbutton.setStyleSheet(
                "background-color: green; color: black"
            )

        else:
            self.switchHeaterZbutton.setText("OFF")
            self.switchHeaterZbutton.setStyleSheet(
                "background-color: red; color: black"
            )
        
        now = datetime.now()
        now.strftime('%Y-%m-%d %H:%M:%S')
        self.switchHeaterZLineEdit.setText(str(now))