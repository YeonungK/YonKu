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
        self.directory_path = pathlib.Path(f"C:/Users/szkop/OneDrive/Desktop/YonKu/Tools/saved_instruments/Members/{self.instrument.model}")
        self.attribute_path =  pathlib.Path(f"C:/Users/szkop/OneDrive/Desktop/YonKu/Tools/saved_instruments/Members/{self.instrument.model}/attributes.py")
        self.edit_button_list = {}
        self.remove_button_list = {}
        
        self.edit_layout = QVBoxLayout(self.editFrame)
        self.edit_layout.setContentsMargins(0, 23, 0, 0)
        self.edit_layout.setSpacing(9)
        self.remove_layout = QVBoxLayout(self.removeFrame)
        self.remove_layout.setContentsMargins(0, 23, 0, 0)
        self.remove_layout.setSpacing(9)
        
        self.fill_command_table()

    def fill_command_table(self):
        # Loop through all items matching the '*.py' pattern in the directory
        for file_path in self.directory_path.glob('*_method.py'):
            with open(file_path, "r") as f:
                command_info_list = f.readlines()
                command_name = command_info_list[1]
                command_name = command_name.replace('command_name = "','')
                command_name = command_name.replace('"\n','')
                
                command_text = command_info_list[2]
                command_text = command_text.replace('command_text = "','')
                command_text = command_text.replace('"\n','')
                
            self.commandListTable.insertRow(0)
            command_name_item = QTableWidgetItem(command_name)
            command_text_item = QTableWidgetItem(command_text)
            self.commandListTable.setItem(0, 0, command_name_item)
            self.commandListTable.setItem(0, 1, command_text_item)
            
            
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
        self.edit_layout.addItem(self.vertical_spacer)
        self.remove_layout.addItem(self.vertical_spacer)
            
    def edit_function(self, command_name):
        self.newCommandWin = QMainWindow()
        self.newCommandWid = ncsu.edit_command_setting_ui(self.instrument, "ETHERNET", self.newCommandWin, command_name)
        self.newCommandWin.setCentralWidget(self.newCommandWid)
        self.newCommandWin.closeEvent = self.newCommandWid.closeEvent
        
        self.newCommandWin.setWindowTitle("Build a new command")
        self.newCommandWin.resize(1000, 800)
        self.newCommandWin.move(200, 200)
        
        self.newCommandWin.show()
        
        self.newCommandWid.newCommandSaveButton.clicked.connect(self.update_command_table)
    
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
        # remove the functions in the attribute file
        attribute_module = importlib.import_module(f"Tools.saved_instruments.Members.{self.instrument.model}.attributes")
        
        functions_dict = getattr(attribute_module, "functions")
        try:
            del functions_dict[command_name]
        except KeyError:
            pass
        functions_dict = "functions = " + str(functions_dict) + "\n"
        
        read_functions_dict = getattr(attribute_module, "read_functions")
        try:
            del read_functions_dict[command_name]
        except KeyError:
            pass
        read_functions_dict = "read_functions = " + str(read_functions_dict) + "\n"
        
        write_functions_dict = getattr(attribute_module, "write_functions")
        try:
            del write_functions_dict[command_name]
        except KeyError:
            pass
        write_functions_dict = "write_functions = " + str(write_functions_dict) + "\n"
        
        try:
            with open(self.attribute_path, "r") as f:
                current_content_list = f.readlines()
                print(current_content_list)
                current_content_list[5] = functions_dict
                current_content_list[6] = read_functions_dict
                current_content_list[7] = write_functions_dict
                
                new_content = ""
                for i in range(0,len(current_content_list)):
                    new_content = new_content + current_content_list[i] 
                
                print(f'Successfully changed.')
            
            with open(self.attribute_path, "w") as f:    
                    f.write(new_content)
        
        except FileNotFoundError:
            print(f"Error: The file '{self.attribute_path}' was not found.")
            
        # Get rid of the import 
        old_import_line = f", {command_name}_method"
        try:
            with open(self.attribute_path, "r") as f:
                current_content = f.read()
                f.seek(0)
                current_content_list = f.readlines()
                print(current_content)
                old_string = current_content_list[2]
                old_string = old_string.replace("\n","")
                new_string = old_string.replace(old_import_line, "")
                
                if old_string not in current_content:
                        print(f'"{old_string}" not found. No changes made.')
                        return

                new_content = current_content.replace(old_string, new_string)
                
                print(f'Successfully changed.')
            
            with open(self.attribute_path, "w") as f:    
                    f.write(new_content)
        
        except FileNotFoundError:
            print(f"Error: The file '{self.attribute_path}' was not found.")
            
            
        # Loop through all items matching the '*.py' pattern in the directory
        removing_file_path = pathlib.Path(f"C:/Users/szkop/OneDrive/Desktop/YonKu/Tools/saved_instruments/Members/{self.instrument.model}/{command_name}_method.py")
        
        try:
            removing_file_path.unlink()
        except Exception as e:
            print(e)
            
        self.update_command_table()
            
        
    
            
            
            
            
            
            
                
                
                