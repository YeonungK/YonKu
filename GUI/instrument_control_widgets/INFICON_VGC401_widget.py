import sys

sys.path.append('C:/Users/szkop/Desktop/YonKu_Editing')


from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5 import uic

class pressureGauge_widget(QWidget):
    def __init__(self):
        super().__init__()
        
        uic.loadUi('GUI/ui_files/instrument_control_uis/INFICON_VGC401_ui.ui', self)
        
        