import sys

sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')


from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5 import uic

class test_widget(QWidget):
    def __init__(self, instrument):
        super().__init__()
        
        self.instrument = instrument
        uic.loadUi('GUI/ui_files/instrument_control_uis/TEST_ui.ui', self)
        
    

        
    
        