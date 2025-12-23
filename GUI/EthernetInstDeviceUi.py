from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget, QFileDialog
from PyQt5 import uic
import sys
from GUI import NewCommandSettingUi as ncsu, CommandListUi as clu

class EthernetnstDeviceUi(QWidget):
    def __init__(self, data_list):
        super().__init__()
        
        uic.loadUi("GUI/ui_files/ethernet_instrument_device_wid.ui", self)
        
        self.instrument = None
        self.nameLabel.setText("Name: " + data_list['name'])
        self.modelLabel.setText("Model: " + data_list['model'])
        self.instrumentIPLabel.setText("Instrument IP Address: " + data_list['instIP'])
        self.portLabel.setText("Port: " + data_list['port'])
        
        self.addCommandButton.clicked.connect(self.new_command_setting)
        self.commandListButton.clicked.connect(self.open_command_list)
        # self.settingButton.clicked.connect(self.open_setting)
    
    def new_command_setting(self):
        self.newCommandWin = QMainWindow()
        self.newCommandWid = ncsu.new_command_setting_ui(self.instrument, "ETHERNET", self.newCommandWin)
        self.newCommandWin.setCentralWidget(self.newCommandWid)
        self.newCommandWin.closeEvent = self.newCommandWid.closeEvent
        
        self.newCommandWin.setWindowTitle("Build a new command")
        self.newCommandWin.resize(1000, 800)
        self.newCommandWin.move(50, 50)
        
        self.newCommandWin.show()
        
        # self.newCommandWid.newCommandSaveButton.clicked.connect(self.save_new_command)
    
    
    def open_command_list(self):
        self.CommandListWin = QMainWindow()
        self.CommandListWid = clu.command_list_ui(self.instrument, self.CommandListWin)
        self.CommandListWin.setCentralWidget(self.CommandListWid)
        
        self.CommandListWin.setWindowTitle(f"{self.instrument.model} Command List")
        self.CommandListWin.resize(600, 420)
        self.CommandListWin.move(500, 200)
        
        self.CommandListWin.show()
    
    # def new_command_setting(self):
    #     self.newCommandWid = NewCommandSettingUi()
    #     self.newCommandWin = QMainWindow()
    #     self.newCommandWin.setWidget = self.newCommandWid
        
    #     self.newCommandWin.setWindowTitle("Add a Serial Instrument")
    #     self.newCommandWin.resize(810, 800)
    #     self.newCommandWin.move(500, 200)
        
    #     self.newCommandWin.show()
        
        
        