
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget, QTableWidgetItem, QVBoxLayout, QSpacerItem, QSizePolicy, QLineEdit
from PyQt5.QtGui import QCloseEvent
from PyQt5 import uic
import json
import sys
import re
import types
import pathlib
import importlib

from GUI import NewCommandSettingUi as ncsu

from project_paths import GUI_DIR, SAVED_INSTRUMENTS_DIR

class command_list_ui(QWidget):
    def __init__(self, instrument, window, ui_edit_list=False, ui_command_lineEdit = None):
        super().__init__()
        print("This works.")
        uic.loadUi(f"{GUI_DIR}/ui_files/command_list.ui", self)
        
        self.instrument = instrument
        self.window = window
        self.ui_edit_list = ui_edit_list
        self.ui_command_lineEdit = ui_command_lineEdit
        self.column_count = self.commandListTable.columnCount()
        self.row_count = self.commandListTable.rowCount()
        
        # Set the path to the current directory ('.') or a specific path
        self.directory_path = SAVED_INSTRUMENTS_DIR / self.instrument.model / "methods"
        self.metadata_path = SAVED_INSTRUMENTS_DIR / self.instrument.model / "metadata.json"
        self.edit_button_list = {}
        self.remove_button_list = {}
        self.pick_button_list = {}
        
        if self.ui_edit_list:
            self.pick_layout = QVBoxLayout(self.editFrame)
            self.pick_layout.setContentsMargins(0, 23, 0, 0)
            self.pick_layout.setSpacing(9)
            
        else:
            self.edit_layout = QVBoxLayout(self.editFrame)
            self.edit_layout.setContentsMargins(0, 23, 0, 0)
            self.edit_layout.setSpacing(9)
            self.remove_layout = QVBoxLayout(self.removeFrame)
            self.remove_layout.setContentsMargins(0, 23, 0, 0)
            self.remove_layout.setSpacing(9)
        
        self.fill_command_table()

    def fill_command_table(self):
        # Loop through all items matching the '*.py' pattern in the directory
        for file_path in self.directory_path.glob('*.py'):
            if file_path.name == "__init__.py":
                continue

            with open(file_path, "r") as f:
                command_info_list = f.readlines()
                
                command_name = file_path.stem
                
                command_text = command_info_list[2]
                command_text = command_text.replace('command_text = "','')
                command_text = command_text.replace('"\n','')
                
            self.commandListTable.insertRow(0)
            command_name_item = QTableWidgetItem(command_name)
            command_text_item = QTableWidgetItem(command_text)
            self.commandListTable.setItem(0, 0, command_name_item)
            self.commandListTable.setItem(0, 1, command_text_item)
            
            if self.ui_edit_list: # if you opened the list from ui_edit_setting
                
                pick_button = QPushButton("Pick")
                setattr(self, f"{command_name}_pick_button", pick_button)
                self.pick_layout.addWidget(pick_button)
                self.pick_button_list[f"{command_name}_pick_button"] = pick_button
                
                
                pick_button.clicked.connect(lambda: self.pick_function(command_name))
            
            else:
                edit_button = QPushButton("Edit")
                setattr(self, f"{command_name}_edit_button", edit_button)
                self.edit_layout.addWidget(edit_button)
                self.edit_button_list[f"{command_name}_edit_button"] = edit_button
                
                
                edit_button.clicked.connect(lambda: self.edit_function(command_name))
                
                
                remove_button = QPushButton("Remove")
                setattr(self, f"{command_name}_cancel_button", remove_button)
                self.remove_layout.addWidget(remove_button)
                self.remove_button_list[f"{command_name}_edit_button"] = remove_button
                
                remove_button.clicked.connect(lambda: self.remove_function(command_name))
            
        self.vertical_spacer = QSpacerItem(15, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        # Add the spacer item to the layout
        if self.ui_edit_list:
            self.pick_layout.addItem(self.vertical_spacer)
        else:
            self.edit_layout.addItem(self.vertical_spacer)
            self.remove_layout.addItem(self.vertical_spacer)
            
    def edit_function(self, command_name):
        # self.newCommandWin = QMainWindow()
        # self.newCommandWid = ncsu.edit_command_setting_ui(self.instrument, "ETHERNET", self.newCommandWin, command_name)
        # self.newCommandWin.setCentralWidget(self.newCommandWid)
        # self.newCommandWin.closeEvent = self.newCommandWid.closeEvent
        
        # self.newCommandWin.setWindowTitle("Build a new command")
        # self.newCommandWin.resize(1000, 800)
        # self.newCommandWin.move(200, 200)
        
        # self.newCommandWin.show()
        
        # self.newCommandWid.newCommandSaveButton.clicked.connect(self.update_command_table)
        print("Command editing is temporarily disabled during metadata refactor.")
    
    def update_command_table(self):
        for name, button in self.edit_button_list.items():
            button.setParent(None)
        for name, button in self.remove_button_list.items():
            button.setParent(None)    
        self.edit_layout.removeItem(self.vertical_spacer)
        self.remove_layout.removeItem(self.vertical_spacer)
        self.commandListTable.clearContents()
        self.commandListTable.setRowCount(0)
        
        self.fill_command_table()
    
    def remove_function(self, command_name):

        removing_file_path = (
            SAVED_INSTRUMENTS_DIR
            / self.instrument.model
            / "methods"
            / f"{command_name}.py"
        )
        
        try:
            removing_file_path.unlink()
        except Exception as e:
            print(e)

        # also remove the command from the metadata

        with open(self.metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        metadata.get("methods", {}).pop(command_name, None)

        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)

            
        self.update_command_table()
        
    def pick_function(self, command_name):
        self.ui_command_lineEdit.setText(command_name)
        self.window.close()
            
        
    
            
            
            
            
            
            
                
                
                