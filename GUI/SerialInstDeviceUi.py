from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget, QFileDialog
from PyQt5 import uic
import sys

class SerialInstDeviceUi(QWidget):
    def __init__(self, data_list):
        super().__init__()
        
        uic.loadUi("GUI/ui_files/serial_instrument_device_wid.ui", self)
        
        self.nameLabel.setText("Name: " + data_list['name'])
        self.modelLabel.setText("Model: " + data_list['model'])
        self.portLabel.setText("Port: " + data_list['port'])
        self.baudrateLabel.setText("Baudrate: " + data_list['baudrate'])
        self.bytesizeLabel.setText("Model: " + data_list['bytesize'])
        self.parityLabel.setText("Parity: " + data_list['parity'])
        self.stopbitsLabel.setText("Stopbits: " + data_list['stopbits'])
        
        
    