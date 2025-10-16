from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget, QFileDialog
from PyQt5 import uic
import sys

class usb6525InstDeviceUi(QWidget):
    def __init__(self, data_list):
        super().__init__()
        
        uic.loadUi("GUI/ui_files/usb_6525_instrument_device_wid.ui", self)
        
        self.nameLabel.setText("Name: " + data_list['name'])
        self.modelLabel.setText("Model: " + data_list['model'])
        
        device_number = "Dev" + data_list['deviceNumber']
        
        self.deviceNumberLabel.setText("Device Number: " + device_number)
        
        port = "port" + data_list['port']
        
        self.portLabel.setText("Port: " + port)
        
        range = data_list['range1'] + ':' + data_list['range2']
        self.rangeLabel.setText("Range: " + range)