import sys

sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')


from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5 import uic
from functools import partial
import os

class test_instrument_widget(QWidget):
    def __init__(self, instrument):
        super().__init__()
        
        self.instrument = instrument
        self.instrument_model = self.instrument.model
        self.instrument_name = self.instrument.name
        uic.loadUi('GUI/ui_files/instrument_control_uis/test_model_ui.ui', self)
        
        
    def bind_dynamic_signals(self):
        
        json_path = f"GUI/instrument_control_widgets/ui_files/instrument_control_uis/{self.instrument_model}_ui.json"
        
        if not os.path.exists(json_path):
            print(f"[ERROR] UI definition file not found: {json_path}")
            return
        
        # Load JSON
        try:
            