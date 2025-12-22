from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget, QFileDialog
from PyQt5 import uic
import sys
from GUI import NewCommandSettingUi as ncsu

class GPIBInstDeviceUi(QWidget):
    def __init__(self, data_list):
        super().__init__()
        
        uic.loadUi("GUI/ui_files/gpib_instrument_device_wid.ui", self)
        
        self.instrument = None
        self.nameLabel.setText("Name: " + data_list['name'])
        self.modelLabel.setText("Model: " + data_list['model'])
        self.addressLabel.setText("Address: " + data_list['address'])
        
        self.addCommandButton.clicked.connect(self.new_command_setting)
        # self.commandListButton.clicked.connect(self.open_command_list)
        # self.settingButton.clicked.connect(self.open_setting)
    
    def new_command_setting(self):
        self.newCommandWid = ncsu.new_command_setting_ui(self.instrument, "GPIB")
        self.newCommandWin = QMainWindow()
        self.newCommandWin.setCentralWidget(self.newCommandWid)
        self.newCommandWin.closeEvent = self.newCommandWid.closeEvent
        
        self.newCommandWin.setWindowTitle("Build a new command")
        self.newCommandWin.resize(810, 800)
        self.newCommandWin.move(200, 200)
        
        self.newCommandWin.show()
        