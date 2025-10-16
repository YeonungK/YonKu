from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget, QFileDialog
from PyQt5 import uic
import sys

class EthernetnstDeviceUi(QWidget):
    def __init__(self, data_list):
        super().__init__()
        
        uic.loadUi("GUI/ui_files/ethernet_instrument_device_wid.ui", self)
        
        self.nameLabel.setText("Name: " + data_list['name'])
        self.modelLabel.setText("Model: " + data_list['model'])
        self.instrumentIPLabel.setText("Instrument IP Address: " + data_list['instIP'])
        self.portLabel.setText("Port: " + data_list['port'])
        