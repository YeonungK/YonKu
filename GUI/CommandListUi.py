from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget, QTableWidgetItem, QVBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QCloseEvent
from PyQt5 import uic
import sys
import re
import types
import pathlib
import importlib
from GUI import NewCommandSettingUi as ncsu

sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')


class command_list_ui(QWidget):
    def __init__(self, instrument, window):
        super().__init__()
        print("This works.")
        uic.loadUi("GUI/ui_files/command_list.ui", self)
        
        self.instrument = instrument
        self.window = window
        self.column_count = self.commandListTable.columnCount()
        self.row_count = self.commandListTable.rowCount()
        
        # Set the path to the current directory ('.') or a specific path
        directory_path = pathlib.Path(f"C:/Users/szkop/OneDrive/Desktop/YonKu/Tools/saved_instruments/Members/{self.instrument.model}") 
        
        edit_layout = QVBoxLayout(self.editFrame)
        edit_layout.setContentsMargins(0, 23, 0, 0)
        edit_layout.setSpacing(9)
        remove_layout = QVBoxLayout(self.removeFrame)
        remove_layout.setContentsMargins(0, 23, 0, 0)
        remove_layout.setSpacing(9)

        # Loop through all items matching the '*.py' pattern in the directory
        for file_path in directory_path.glob('*_method.py'):
            with open(file_path, "r") as f:
                command_info_list = f.readlines()
                command_name = command_info_list[1]
                command_name = command_name.replace('command_name = "','')
                command_name = command_name.replace('"\n','')
                
                command_text = command_info_list[2]
                command_text = command_text.replace('command_text = "','')
                command_text = command_text.replace('"\n','')
                
            self.commandListTable.insertRow(self.row_count)
            command_name_item = QTableWidgetItem(command_name)
            command_text_item = QTableWidgetItem(command_text)
            self.commandListTable.setItem(self.row_count-0, 0, command_name_item)
            self.commandListTable.setItem(self.row_count-0, 1, command_text_item)
            
            
            edit_button = QPushButton("Edit")
            setattr(self, f"{command_name}_edit_button", edit_button)
            edit_layout.addWidget(edit_button)
            
            
            edit_button.clicked.connect(lambda: self.edit_function(command_name))
            
            
            remove_button = QPushButton("Cancel")
            setattr(self, f"{command_name}_cancel_button", remove_button)
            remove_layout.addWidget(remove_button)
            
        vertical_spacer = QSpacerItem(15, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        # Add the spacer item to the layout
        edit_layout.addItem(vertical_spacer)
        remove_layout.addItem(vertical_spacer)
            
    def edit_function(self, command_name):
        self.newCommandWin = QMainWindow()
        self.newCommandWid = ncsu.edit_command_setting_ui(self.instrument, "ETHERNET", self.newCommandWin, command_name)
        self.newCommandWin.setCentralWidget(self.newCommandWid)
        self.newCommandWin.closeEvent = self.newCommandWid.closeEvent
        
        self.newCommandWin.setWindowTitle("Build a new command")
        self.newCommandWin.resize(1000, 800)
        self.newCommandWin.move(200, 200)
        
        self.newCommandWin.show()
            
            
            
            
            
                
                
                