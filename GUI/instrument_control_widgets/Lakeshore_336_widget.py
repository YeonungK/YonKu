from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget
from PyQt5 import uic
import sys

sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')


class temperatureController_widget(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("GUI/ui_files/instrument_control_uis/Lakeshore_336_ui.ui", self)
        
        
        self.unitSwitchButton.clicked.connect(self.switch_unit)
        
    def switch_unit(self):
        if self.unitSwitchButton.isChecked():
            self.unitSwitchButton.setText("Current Unit: Temperature (K)")
        else:
            self.unitSwitchButton.setText("Current Unit: Resistance (Ohms)")
        
        