from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget, QFileDialog
from PyQt5.QtGui import QCloseEvent
from PyQt5 import uic
import sys


class DeviceListUi(QMdiSubWindow):
    def __init__(self,mdi):
        super().__init__()
        
        self.widget = QWidget()
        uic.loadUi("GUI/ui_files/device_list.ui", self.widget)
        
        
        mdi.addSubWindow(self)
        self.setWidget(self.widget)
        self.setWindowTitle("Device List")
        self.resize(350, 450)

        
    def closeEvent(self, event:QCloseEvent):
        pass
        
        