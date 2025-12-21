from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget
from PyQt5.QtGui import QCloseEvent
from PyQt5 import uic
import sys
import re
import types
import pathlib
import importlib

sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')


class new_command_setting_ui(QWidget):
    _GENERIC_NAME_RE = re.compile(r".*_\d+$")
    
    def __init__(self, instrument):
        super().__init__()
        print("loadUi")
        uic.loadUi("GUI/ui_files/new_command.ui", self)
        
        self.instrument = instrument
        
        self.save_file = False
        # self.interface = str(interface)
        
        # ===== QLabel contents =====
        # # self.comInterfaceLabel.setText(self.interface)
        # self.commandTypeInstr = self.commandTypeInstr.text()

        # ===== QLineEdit contents =====
        self.command_name = self.nameLineEdit.text()
        self.command_text = self.commandText.text()
        # self.dataDefaultValue = self.dataDefaultValue.text()
        # self.writeLineEdit = self.writeLineEdit.text()
        # self.queryLineEdit = self.queryLineEdit.text()
        # self.sleepLineEdit = self.sleepLineEdit.text()
        # self.testValue = self.testValue.text()
        # self.testResponse = self.testResponse.text()
        # self.dataManLineEdit1 = self.dataManLineEdit1.text()
        # self.dataManLineEdit2 = self.dataManLineEdit2.text()
        # self.dataManCurrentResponse = self.dataManCurrentResponse.text()

        # # ===== QComboBox contents =====
        # self.dataTypeComboBox = self.dataTypeComboBox.currentText()
        # self.commandTypeComboBox = self.commandTypeComboBox.currentText()
        # self.comSystemComboBox = self.comSystemComboBox.currentText()
        # self.testComboBox = self.testComboBox.currentText()
        # self.desiredDataComboBox = self.desiredDataComboBox.currentText()
        # self.dataManComboBox = self.dataManComboBox.currentText()
        
        self.function_code = ""
        self.data_manipulation_code = ""
        
        self.create_member_folder()

        # # ===== QPushButton contents =====
        # self.dataTypeAddButton = self.dataTypeAddButton.text()
        # self.dataTypeSaveButton = self.dataTypeSaveButton.text()
        # self.dataTypeRemoveButton = self.dataTypeRemoveButton.text()

        # self.writeAddButton = self.writeAddButton.text()
        # self.readAddButton = self.readAddButton.text()
        # self.queryAddButton = self.queryAddButton.text()
        # self.sleepAddButton = self.sleepAddButton.text()

        # self.functionSave = self.functionSave.text()
        # self.functionClear = self.functionClear.text()
        # self.functionEdit = self.functionEdit.text()
        # self.functionSaveAsTemplate = self.functionSaveAsTemplate.text()
        # self.functionImportTemplate = self.functionImportTemplate.text()

        # self.testSave = self.testSave.text()
        # self.testExecute = self.testExecute.text()

        # self.dataManAddButton = self.dataManAddButton.text()
        # self.dataManSave = self.dataManSave.text()
        # self.dataManClear = self.dataManClear.text()
        # self.dataManEdit = self.dataManEdit.text()
        # self.dataManSaveAsTemplate = self.dataManSaveAsTemplate.text()
        # self.dataManImportTemplate = self.dataManImportTemplate.text()
        
        
        
        self._connect_pushbuttons()
    
    def create_member_folder(self):
        
        print("creating folders")
        instrument_folder = pathlib.Path(f"C:/Users/szkop/OneDrive/Desktop/YonKu/Tools/saved_instruments/Members/{self.instrument.model}")
        instrument_folder.mkdir(parents=True, exist_ok=True)
        
        instrument_attribute = pathlib.Path(f"C:/Users/szkop/OneDrive/Desktop/YonKu/Tools/saved_instruments/Members/{self.instrument.model}/attributes.py")
        
        if not instrument_attribute.exists():
            instrument_attribute.touch()
            with open(instrument_attribute, "w") as f:
                basic_attributes = f"""
data_type = {{}}
data_unit = {{}}
functions = {{}}
read_functions = {{}}
write_functions = {{}}
data_functions = {{}}
initial_state = {{}}
"""
                f.write(basic_attributes)
                f.close()
        else:
            pass
        
        self.method_name = self.command_name
        index = self.try_make_method_file(self.method_name, 0)
        self.method_name = self.method_name + "_" + str(index)
        self.method_path = pathlib.Path(f"C:/Users/szkop/OneDrive/Desktop/YonKu/Tools/saved_instruments/Members/{self.instrument.model}/{self.method_name}_method.py")
        
        with open(self.method_path, "w") as f:
            script = f"""
command_name = "{self.command_name}"
command_text = "{self.command_text}"
data_list = {{}}
command_type = "{self.commandTypeComboBox.currentText()}"
communication_syntax = "{self.comSystemComboBox.currentIndex()}"
desired_data_type = "{self.desiredDataComboBox.currentText()}"

function_code = ""
data_manipulation_code = ""
            """
            f.write(script)
            f.close()
        
        
        
        
    def try_make_method_file(self, method_name, num):
        method_real_name = method_name + "_" + str(num)
        method_path = pathlib.Path(f"C:/Users/szkop/OneDrive/Desktop/YonKu/Tools/saved_instruments/Members/{self.instrument.model}/{method_real_name}_method.py")
        try:
            method_path.touch()
            index = num
        except FileExistsError:
            num += 1
            index = self.try_make_method_file(method_name, num)
        return index
        
    def _connect_pushbuttons(self):
        """
        Auto-connect QPushButton.clicked to
        self.<objectName>_method
        """
        for button in self.findChildren(QPushButton):
            name = button.objectName()

            if not name or self._GENERIC_NAME_RE.match(name):
                continue

            method_name = f"{name}_method"

            # Create a stub if it does not exist
            if not hasattr(self, method_name):
                setattr(
                    self,
                    method_name,
                    types.MethodType(self._default_button_method, self)
                )

            button.clicked.connect(getattr(self, method_name))
    
    def _default_button_method(self):
        sender = self.sender()
        print(f"[DEBUG] {sender.objectName()} clicked")
    
    def nameSaveButton_method(self):
        
        new_method_path = pathlib.Path(f"C:/Users/szkop/OneDrive/Desktop/YonKu/Tools/saved_instruments/Members/{self.instrument.model}/{self.nameLineEdit.text()}_method.py")
        try:
            self.method_path.rename(new_method_path)
            
            with open(new_method_path, "r") as f:
                current_content = f.read()
                print(current_content)
                old_string = f'command_name = "{self.command_name}"'
                new_string = f'command_name = "{self.nameLineEdit.text()}"'
                
                if old_string not in current_content:
                    print(f'"{old_string}" not found. No changes made.')
                    return
                
                new_content = current_content.replace(old_string, new_string)
                print(f'Successfully changed "{old_string}" to "{new_string}".')
                
            with open(new_method_path, "w") as f:    
                f.write(new_content)
            
            self.command_name = self.nameLineEdit.text()
            self.method_path = new_method_path
                
        except FileNotFoundError:
            print(f"Error: The file '{self.method_path}' was not found.")
        except FileExistsError:
            self.nameLineEdit.setText(f"This name already exists.")
            print(f"Error: The file '{self.command_name}' already exists.")
        
                    

                
        
    def commandTextSaveButton_method(self):
        pass
    # -------------------------------
    # Data type buttons
    # -------------------------------
    def dataTypeAddButton_method(self):
        pass

    def dataTypeSaveButton_method(self):
        pass

    def dataTypeRemoveButton_method(self):
        pass

    # -------------------------------
    # WRITE / READ / QUERY / SLEEP
    # -------------------------------
    def writeAddButton_method(self):
        pass

    def readAddButton_method(self):
        pass

    def queryAddButton_method(self):
        pass

    def sleepAddButton_method(self):
        pass

    # -------------------------------
    # Function builder buttons
    # -------------------------------
    def functionSave_method(self):
        pass

    def functionClear_method(self):
        pass

    def functionEdit_method(self):
        pass

    def functionSaveAsTemplate_method(self):
        pass

    def functionImportTemplate_method(self):
        pass

    # -------------------------------
    # Test section buttons
    # -------------------------------
    def testSave_method(self):
        pass

    def testExecute_method(self):
        pass

    # -------------------------------
    # Data manipulation buttons
    # -------------------------------
    def dataManAddButton_method(self):
        pass

    def dataManSave_method(self):
        pass

    def dataManClear_method(self):
        pass

    def dataManEdit_method(self):
        pass

    def dataManSaveAsTemplate_method(self):
        pass

    def dataManImportTemplate_method(self):
        pass
    
    def newCommandCancelButton_method(self):
        #print("the cancel button works")
        self.closeEvent(QCloseEvent)
    
    def closeEvent(self, event:QCloseEvent):
        #print("this is working")
        self.method_path.unlink()
        event.accept()