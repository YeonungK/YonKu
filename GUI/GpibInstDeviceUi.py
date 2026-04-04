from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget, QFileDialog
from PyQt5 import uic
import sys
from GUI import NewCommandSettingUi as ncsu, CommandListUi as clu, ConnectWarningUi as cwu, UiEditUi as udu
import os
import shutil
import stat

sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')

class GPIBInstDeviceUi(QWidget):
    def __init__(self, data_list):
        super().__init__()
        
        uic.loadUi("GUI/ui_files/gpib_instrument_device_wid.ui", self)
        
        self.instrument = None
        self.data_list = data_list
        self.nameLabel.setText("Name: " + data_list['name'])
        self.modelLabel.setText("Model: " + data_list['model'])
        self.addressLabel.setText("Address: " + data_list['address'])
        
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
            self.newCommandWid = ncsu.new_command_setting_ui(self.instrument, "GPIB", self.newCommandWin)
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
            self.newUiWid = udu.ui_edit_setting_ui(self.instrument, self.data_list, "GPIB", self.newUiWin)
            self.newUiWin.setCentralWidget(self.newUiWid)
            self.newUiWin.closeEvent = self.newUiWid.closeEvent
            
            self.newUiWin.setWindowTitle("Edit the UI")
            self.newUiWin.resize(1000, 800)
            self.newUiWin.move(50, 50)
            
            self.newUiWin.show()
            
    def remove_instrument_confirm(self):
        removeInstrumentWid = QWidget()
        uic.loadUi("GUI/ui_files/remove_instrument_confirm.ui", removeInstrumentWid)
        self.removeInstrumentWin = QMainWindow()
        self.removeInstrumentWin.setCentralWidget(removeInstrumentWid)
        self.removeInstrumentWin.setWindowTitle("Remove this instrument")
        self.removeInstrumentWin.resize(550, 200)
        self.removeInstrumentWin.move(600, 400)
        self.removeInstrumentWin.show()
        
        removeInstrumentWid.removeInstButton.clicked.connect(self.remove_instrument)
        removeInstrumentWid.cancelButton.clicked.connect(self.removeInstrumentWin.hide)
    
    def remove_readonly(self, func, path, _):
        "Clear the readonly bit and reattempt the removal"
        os.chmod(path, stat.S_IWRITE)
        func(path)


    
    def remove_instrument(self):
        instrument_model = self.data_list['model']
        
        # remove the instrument related files
        
        #1. the instrument object python file
        
        path = f"Tools/saved_instruments/{instrument_model}.py"
        if os.path.isfile(path):
            os.remove(path)
        else:
            print("Error: %s file not found" % path)
        
        #2. the command/attribute folder of the instrument
        
        path = f"Tools/saved_instruments/Members/{instrument_model}"
        if os.path.isdir(path):
            shutil.rmtree(path, onerror=self.remove_readonly)
        else:
            print("Error: %s file not found" % path)
            
        #3. the instrument widget python file
        
        path = f"GUI/instrument_control_widgets/{instrument_model}_widget.py"
        if os.path.isfile(path):
            os.remove(path)
        else:
            print("Error: %s file not found" % path)
        
        #4. the instrument ui file
        
        path = f"GUI/ui_files/instrument_control_uis/{instrument_model}_ui.ui"
        if os.path.isfile(path):
            os.remove(path)
        else:
            print("Error: %s file not found" % path)
            
        self.removeInstrumentWin.close()