from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget, QFileDialog
from PyQt5 import uic
import sys
from GUI import NewCommandSettingUi as ncsu

class usb6525InstDeviceUi(QWidget):
    def __init__(self, data_list):
        super().__init__()
        
        uic.loadUi("GUI/ui_files/usb_6525_instrument_device_wid.ui", self)
        
        self.instrument = None
        self.nameLabel.setText("Name: " + data_list['name'])
        self.modelLabel.setText("Model: " + data_list['model'])
        
        device_number = "Dev" + data_list['deviceNumber']
        
        self.deviceNumberLabel.setText("Device Number: " + device_number)
        
        port = "port" + data_list['port']
        
        self.portLabel.setText("Port: " + port)
        
        range = data_list['range1'] + ':' + data_list['range2']
        self.rangeLabel.setText("Range: " + range)
        
        self.addCommandButton.clicked.connect(self.new_command_setting)
        # self.commandListButton.clicked.connect(self.open_command_list)
        # self.settingButton.clicked.connect(self.open_setting)
    
    def new_command_setting(self):
        self.newCommandWin = QMainWindow()
        self.newCommandWid = ncsu.new_command_setting_ui(self.instrument, "USB6525", self.newCommandWin)
        self.newCommandWin.setCentralWidget(self.newCommandWid)
        self.newCommandWin.closeEvent = self.newCommandWid.closeEvent
        
        self.newCommandWin.setWindowTitle("Build a new command")
        self.newCommandWin.resize(1000, 800)
        self.newCommandWin.move(50, 50)
        
        self.newCommandWin.show()