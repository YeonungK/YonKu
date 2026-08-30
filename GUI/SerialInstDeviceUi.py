from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget, QFileDialog
from PyQt5 import uic
import sys
from GUI import NewCommandSettingUi as ncsu, CommandListUi as clu, ConnectWarningUi as cwu, UiEditUi as udu
from pathlib import Path
from project_paths import GUI_DIR
from Tools.DeviceRemover import remove_device

class SerialInstDeviceUi(QWidget):
    def __init__(self, data_list, config_path=None):
        super().__init__()
        
        uic.loadUi(f"{GUI_DIR}/ui_files/serial_instrument_device_wid.ui", self)
        
        self.instrument = None
        self.data_list = data_list
        self.config_path = Path(config_path) if config_path else None
        self.nameLabel.setText("Name: " + data_list['name'])
        self.modelLabel.setText("Model: " + data_list['model'])
        self.portLabel.setText("Port: " + data_list['port'])
        self.baudrateLabel.setText("Baudrate: " + data_list['baudrate'])
        self.bytesizeLabel.setText("Model: " + data_list['bytesize'])
        self.parityLabel.setText("Parity: " + data_list['parity'])
        self.stopbitsLabel.setText("Stopbits: " + data_list['stopbits'])
        
        self.addCommandButton.clicked.connect(self.new_command_setting)
        self.commandListButton.clicked.connect(self.open_command_list)
        self.editWidgetButton.clicked.connect(self.ui_edit_setting)
        self.removeDeviceButton.clicked.connect(self.remove_instrument_confirm)
    
    def new_command_setting(self):
        if self.instrument == None:
            self.warningWid = cwu.connect_warning_ui()
            self.warningWid.show()
        else:
            self.newCommandWin = QMainWindow()
            self.newCommandWid = ncsu.new_command_setting_ui(self.instrument, "SERIAL", self.newCommandWin)
            self.newCommandWin.setCentralWidget(self.newCommandWid)
            self.newCommandWin.closeEvent = self.newCommandWid.closeEvent
            
            self.newCommandWin.setWindowTitle("Build a new command")
            self.newCommandWin.resize(1000, 800)
            self.newCommandWin.move(50, 50)
            
            self.newCommandWin.show()
        
        # self.newCommandWid.newCommandSaveButton.clicked.connect(self.save_new_command)
    
    
    def open_command_list(self):
        if self.instrument == None:
            self.warningWid = cwu.connect_warning_ui()
            self.warningWid.show()
        else:
            self.CommandListWin = QMainWindow()
            self.CommandListWid = clu.command_list_ui(self.instrument, self.CommandListWin)
            self.CommandListWin.setCentralWidget(self.CommandListWid)
            
            self.CommandListWin.setWindowTitle(f"{self.instrument.model} Command List")
            self.CommandListWin.resize(600, 420)
            self.CommandListWin.move(500, 200)
            
            self.CommandListWin.show()
            
    def ui_edit_setting(self):
        if self.instrument == None:
            self.warningWid = cwu.connect_warning_ui()
            self.warningWid.show()
        else:
            self.newUiWin = QMainWindow()
            self.newUiWid = udu.ui_edit_setting_ui(self.instrument, self.data_list, "SERIAL", self.newUiWin)
            self.newUiWin.setCentralWidget(self.newUiWid)
            self.newUiWin.closeEvent = self.newUiWid.closeEvent
            
            self.newUiWin.setWindowTitle("Edit the UI")
            self.newUiWin.resize(1000, 800)
            self.newUiWin.move(50, 50)
            
            self.newUiWin.show()
            
    def remove_instrument_confirm(self):
        removeInstrumentWid = QWidget()
        uic.loadUi(f"{GUI_DIR}/ui_files/remove_instrument_confirm.ui", removeInstrumentWid)
        self.removeInstrumentWin = QMainWindow()
        self.removeInstrumentWin.setCentralWidget(removeInstrumentWid)
        self.removeInstrumentWin.setWindowTitle("Remove this instrument")
        self.removeInstrumentWin.resize(550, 200)
        self.removeInstrumentWin.move(600, 400)
        self.removeInstrumentWin.show()
        
        removeInstrumentWid.removeInstButton.clicked.connect(self.remove_instrument)
        removeInstrumentWid.cancelButton.clicked.connect(self.removeInstrumentWin.hide)



    def remove_instrument(self):
        if self.config_path is None:
            print("Error: saved-device config path is unavailable")
            return
        remove_device(self.data_list['model'], self.config_path)
        self.removeInstrumentWin.close()
