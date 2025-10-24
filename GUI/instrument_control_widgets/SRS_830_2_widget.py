from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget
from PyQt5 import uic
from PyQt5.QtGui import QCloseEvent
import sys

import sys

sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')


class lockInAmplifier2_widget(QWidget):
    def __init__(self):
        super().__init__()
        
        uic.loadUi("GUI/ui_files/instrument_control_uis/SRS_830_ui.ui", self)
        
    def closeEvent(self, event: QCloseEvent):
        pass
        