from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget
from PyQt5.QtGui import QCloseEvent
from PyQt5 import uic
import sys
import re
import types
import pathlib
import importlib
import shutil
import os
from GUI import ManualEditUi as meu

sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')


class new_command_setting_ui(QWidget):
    _GENERIC_NAME_RE = re.compile(r".*_\d+$")
    
    def __init__(self, instrument, interface, window):
        super().__init__()
        print("loadUi")
        uic.loadUi("GUI/ui_files/new_command.ui", self)
        
        self.instrument = instrument
        
        self.save_file = False
        self.interface = str(interface)
        self.window = window
        
        # ===== QLabel contents =====
        self.comInterfaceLabel.setText(self.interface)
        # self.commandTypeInstr = self.commandTypeInstr.text()

        # ===== QLineEdit contents =====
        self.command_name = self.nameLineEdit.text()
        self.command_text = self.commandText.text()
        self.old_data_list = {}
        self.new_data_list = {}
        
        self.old_test_data_list = {}
        self.new_test_data_list = {}
        
        self.command_type = self.commandTypeComboBox.currentText()
        self.communication_syntax = self.comSystemComboBox.currentText()
       
        self.old_function_code = ""
        self.new_function_code = ""
        
        self.old_data_manipulation_code = ""
        self.new_data_manipulation_code = ""
        
        self.writeCommandCheckBox.stateChanged.connect(self.writeCommandCheckBox_method)
        self.queryCommandCheckBox.stateChanged.connect(self.queryCommandCheckBox_method)
        self.dataComboBox.currentIndexChanged.connect(self.change_data_default)
        self.testComboBox.currentIndexChanged.connect(self.change_test_data_default)
        self.dataManComboBox.currentIndexChanged.connect(self.change_data_man_line_setting)
        
        self.method_script = ""
        self.response = ""
        self.man_response = ""
        self.returning_variable_name = "response"

        self.desiredDataInstr.setText("")
        
        self.create_member_folder()
        self._connect_pushbuttons()
    
    def create_member_folder(self):
        
        print("creating folders")
        instrument_folder = pathlib.Path(f"C:/Users/szkop/OneDrive/Desktop/YonKu/Tools/saved_instruments/Members/{self.instrument.model}")
        instrument_folder.mkdir(parents=True, exist_ok=True)
        
        self.attribute_path = pathlib.Path(f"C:/Users/szkop/OneDrive/Desktop/YonKu/Tools/saved_instruments/Members/{self.instrument.model}/attributes.py")
        
        if not self.attribute_path.exists():
            self.attribute_path.touch()
            with open(self.attribute_path, "w") as f:
                basic_attributes = f"""import sys
sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')
from Tools.saved_instruments.Members.{self.instrument.model} import attributes
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
data_list = {self.old_data_list}
command_type = "{self.command_type}"
communication_syntax = "{self.communication_syntax}"
desired_data_type = "{self.desiredDataComboBox.currentText()}"

function_code = \"\"\"{self.old_function_code}\"\"\"
data_manipulation_code = \"\"\"{self.old_data_manipulation_code}\"\"\"
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
        try:
            with open(self.method_path, "r") as f:
                current_content = f.read()
                print(current_content)
                old_string = f'command_text = "{self.command_text}"'
                new_string = f'command_text = "{self.commandText.text()}"'
                
                if old_string not in current_content:
                        print(f'"{old_string}" not found. No changes made.')
                        return

                new_content = current_content.replace(old_string, new_string)
                print(f'Successfully changed "{old_string}" to "{new_string}".')
            
            with open(self.method_path, "w") as f:    
                    f.write(new_content)
            
            self.command_text = self.commandText.text()
        
        except FileNotFoundError:
            print(f"Error: The file '{self.method_path}' was not found.")
        
    # -------------------------------
    # Data type buttons
    # -------------------------------
    def dataAddButton_method(self):
        data_name = "Data" + str(self.dataComboBox.count())
        self.dataComboBox.addItem(data_name)
        self.testComboBox.addItem(data_name)
        self.new_data_list[data_name] = ""
        self.new_test_data_list[data_name] = ""
        try:
            with open(self.method_path, "r") as f:
                current_content = f.read()
                print(current_content)
                old_string = f'data_list = {self.old_data_list}'
                new_string = f'data_list = {self.new_data_list}'
                
                if old_string not in current_content:
                        print(f'"{old_string}" not found. No changes made.')
                        return

                new_content = current_content.replace(old_string, new_string)
                print(f'Successfully changed "{old_string}" to "{new_string}".')
            
            with open(self.method_path, "w") as f:    
                    f.write(new_content)
            
            self.old_data_list = self.new_data_list
        
        except FileNotFoundError:
            print(f"Error: The file '{self.method_path}' was not found.")

    def dataSaveButton_method(self):
        data_name = self.dataComboBox.currentText()
        self.new_data_list[data_name] = self.dataDefaultValue.text()
        self.new_test_data_list[data_name] = self.dataDefaultValue.text()
        try:
            with open(self.method_path, "r") as f:
                current_content = f.read()
                print(current_content)
                old_string = f'data_list = {self.old_data_list}'
                new_string = f'data_list = {self.new_data_list}'
                
                if old_string not in current_content:
                        print(f'"{old_string}" not found. No changes made.')
                        return

                new_content = current_content.replace(old_string, new_string)
                print(f'Successfully changed "{old_string}" to "{new_string}".')
            
            with open(self.method_path, "w") as f:    
                    f.write(new_content)
            
            self.old_data_list = self.new_data_list
        
        except FileNotFoundError:
            print(f"Error: The file '{self.method_path}' was not found.")
    
    def change_data_default(self):
        self.dataDefaultValue.setText(self.old_data_list[self.dataComboBox.currentText()])

    def dataRemoveButton_method(self):
        data_name = self.dataComboBox.currentText()
        self.dataComboBox.removeItem(self.dataComboBox.currentIndex())
        self.testComboBox.removeItem(self.dataComboBox.currentIndex())
        del self.new_data_list[data_name]
        try:
            with open(self.method_path, "r") as f:
                current_content = f.read()
                print(current_content)
                old_string = f'data_list = {self.old_data_list}'
                new_string = f'data_list = {self.new_data_list}'
                
                if old_string not in current_content:
                        print(f'"{old_string}" not found. No changes made.')
                        return

                new_content = current_content.replace(old_string, new_string)
                print(f'Successfully changed "{old_string}" to "{new_string}".')
            
            with open(self.method_path, "w") as f:    
                    f.write(new_content)
            
            self.old_data_list = self.new_data_list
        
        except FileNotFoundError:
            print(f"Error: The file '{self.method_path}' was not found.")
    
    def commandTypeSaveButton_method(self):
        try:
            with open(self.method_path, "r") as f:
                current_content = f.read()
                print(current_content)
                old_string = f'command_type = "{self.command_type}"'
                new_string = f'command_type = "{self.commandTypeComboBox.currentText()}"'
                
                if old_string not in current_content:
                        print(f'"{old_string}" not found. No changes made.')
                        return

                new_content = current_content.replace(old_string, new_string)
                print(f'Successfully changed "{old_string}" to "{new_string}".')
            
            with open(self.method_path, "w") as f:    
                    f.write(new_content)
            
            self.command_type = self.commandTypeComboBox.currentText()
        
        except FileNotFoundError:
            print(f"Error: The file '{self.method_path}' was not found.")

    # -------------------------------
    # BUILD YOUR FUNCTION
    # -------------------------------
    
    def comSystemSaveButton_method(self):
        try:
            with open(self.method_path, "r") as f:
                current_content = f.read()
                print(current_content)
                old_string = f'communication_syntax = "{self.communication_syntax}"'
                new_string = f'communication_syntax = "{self.comSystemComboBox.currentText()}"'
                
                if old_string not in current_content:
                        print(f'"{old_string}" not found. No changes made.')
                        return

                new_content = current_content.replace(old_string, new_string)
                print(f'Successfully changed "{old_string}" to "{new_string}".')
            
            with open(self.method_path, "w") as f:    
                    f.write(new_content)
            
            self.command_text = self.commandTypeComboBox.currentText()
        
        except FileNotFoundError:
            print(f"Error: The file '{self.method_path}' was not found.")
    
    def writeCommandCheckBox_method(self):
        if self.writeCommandCheckBox.isChecked():
            self.writeLineEdit.setText(self.command_text)
            self.writeLineEdit.setEnabled(False)
        else:
            self.writeLineEdit.setEnabled(True)
        
        
    def writeAddButton_method(self):
        code_line = 'self.write("' + self.writeLineEdit.text() + '")\n'
        self.new_function_code = self.new_function_code + code_line
        self.functionDisplay.setPlainText(self.new_function_code)
        
        

    def readAddButton_method(self):
        variable_name = self.readVariableLineEdit.text()
        code_line = f'{variable_name} = self.read()\n'
        self.new_function_code = self.new_function_code + code_line
        self.functionDisplay.setPlainText(self.new_function_code)

    def queryAddButton_method(self):
        variable_name = self.queryVariableLineEdit.text()
        code_line = f'{variable_name} = self.query("' + self.queryCommandLineEdit.text() + '")\n'
        self.new_function_code = self.new_function_code + code_line
        self.functionDisplay.setPlainText(self.new_function_code)
        
    def queryCommandCheckBox_method(self):
        if self.queryCommandCheckBox.isChecked():
            self.queryCommandLineEdit.setText(self.command_text)
            self.queryCommandLineEdit.setEnabled(False)
        else:
            self.queryCommandLineEdit.setEnabled(True)
        
    def sleepAddButton_method(self):
        sleep_period = self.sleepLineEdit.text()
        try:
            sleep_period = int(sleep_period)
        except:
            self.sleepLineEdit.setText("This period is invalid. The period has to be an integer in seconds.")
        code_line = f'time.sleep({sleep_period})\n'
        self.new_function_code = self.new_function_code + code_line
        self.functionDisplay.setPlainText(self.new_function_code)
    
    def returnAddButton_method(self):
        self.returning_variable_name = self.returnLineEdit.text()
        code_line = f"return {self.returning_variable_name}"
        self.new_function_code = self.new_function_code + code_line
        self.functionDisplay.setPlainText(self.new_function_code)
        

    # -------------------------------
    # Function builder buttons
    # -------------------------------
    def functionDelete_method(self):
        self.new_function_code = self.new_function_code.split("\n")
        n = len(self.new_function_code) - 2
        mid_function_code = ""
        for i  in range(0,n):
            mid_function_code = mid_function_code + self.new_function_code[i] + "\n"
        
        self.new_function_code = mid_function_code
        self.functionDisplay.setPlainText(self.new_function_code)

    def functionClear_method(self):
        self.new_function_code = ""
        self.functionDisplay.setPlainText(self.new_function_code)
        

    def functionEdit_method(self):
        self.manualEditWin = QMainWindow()
        self.manualEditWid = meu.manual_edit_ui(self.new_function_code)
        self.manualEditWin.setCentralWidget(self.manualEditWid)
        self.manualEditWin.closeEvent = self.manualEditWid.closeEvent
        
        self.manualEditWin.setWindowTitle("Manually edit the function")
        self.manualEditWin.resize(350, 350)
        self.manualEditWin.move(500, 300)
        
        self.manualEditWin.show()
        self.manualEditWid.manualEditSave.clicked.connect(self.manual_edit_save)
        self.manualEditWid.manualEditCancel.clicked.connect(self.manualEditWin.close)
    
    def manual_edit_save(self):
        self.new_function_code = self.manualEditWid.code
        self.functionDisplay.setPlainText(self.new_function_code)
        self.manualEditWin.close()
    
        
    def functionSave_method(self):
        try:
            with open(self.method_path, "r") as f:
                current_content = f.read()
                print(current_content)
                old_string = f'function_code = \"\"\"{self.old_function_code}\"\"\"'
                new_string = f'function_code = \"\"\"{self.new_function_code}\"\"\"'
                
                if old_string not in current_content:
                        print(f'"{old_string}" not found. No changes made.')
                        return

                new_content = current_content.replace(old_string, new_string)
                print(f'Successfully changed.')
            
            with open(self.method_path, "w") as f:    
                    f.write(new_content)
            
            self.old_function_code = self.new_function_code
        
        except FileNotFoundError:
            print(f"Error: The file '{self.method_path}' was not found.")

    def functionSaveAsTemplate_method(self):
        pass

    def functionImportTemplate_method(self):
        pass

    # -------------------------------
    # Test section buttons
    # -------------------------------
    def testSave_method(self):
        data_name = self.self.testComboBox.currentText()
        self.new_test_data_list[data_name] = self.testValue.text()
    
    def change_test_data_default(self):
        self.testValue.setText(self.new_test_data_list[self.testComboBox.currentText()])

    def testExecute_method(self):
        function_code = ""
        function_code_list = self.new_function_code.split("\n")
        n = len(function_code_list)
        
        for i in range(0,n):
            function_code = function_code + "        " + function_code_list[i] + "\n"
        
        for data_name, data_value in self.new_test_data_list.items():
            function_code = function_code.replace(f"{{{data_name}}}", data_value)

# ADD THE TEST FUNCTION
        try:
            with open(self.method_path, "a") as f:
                self.method_script = f"""
def {self.command_name}(self):
    try:
{function_code}
    except Exception as e:
        print("Something went wrong: " + e)
"""
                print(self.method_script)
                f.write(self.method_script)     
        except FileNotFoundError:
            print(f"Error: The file '{self.method_path}' was not found.")
# IMPORT AND RUN THE TEST FUNCTION
        try:
            module_path = f"Tools.saved_instruments.Members.{self.instrument.model}.{self.command_name}_method"
            if module_path in sys.modules:
                method_module = importlib.reload(sys.modules[module_path])
            else:
                method_module = importlib.import_module(module_path)
            # 2. Get the specific function/attribute from the module using getattr
            method_function = getattr(method_module, f"{self.command_name}")
            
            self.response = method_function(self.instrument)
            print("This is the respone: " + self.response)
            
            
            
            self.testResponse.setText(self.response)

        except (ImportError, AttributeError) as e:
            print(f"Error: {e}")
        except IndentationError:
            self.testResponse.setText("The function code is empty.")
        except Exception as e:
                self.testResponse.setText(str(e))
                print(str(e))
        
            
# REMOVE THE TEST FUNCTION
        try:
            with open(self.method_path, "r") as f:
                current_content = f.read()
                old_string = self.method_script
                new_string = ""
                
                if old_string not in current_content:
                        print(f'"{old_string}" not found. No changes made.')
                        return

                new_content = current_content.replace(old_string, new_string)
                print(f'Successfully changed.')
            
            with open(self.method_path, "w") as f:    
                    f.write(new_content)
        
        except FileNotFoundError:
            print(f"Error: The file '{self.method_path}' was not found.")
            

    # -------------------------------
    # Data manipulation buttons
    # -------------------------------
    # def dataManCheckButton_method(self):
    #     self.man_response = self.response
    
    def change_data_man_line_setting(self):
        index_number = self.dataManComboBox.currentIndex()
        match index_number:
            case 0:
                self.dataManLineEdit1.setEnabled(True)
                self.dataManLineEdit2.setEnabled(True)
                self.dataManLineEdit1.setPlaceholderText("from")
                self.dataManLineEdit2.setPlaceholderText("to")
                self.dataManInstr.setText("Provide the old and new texts to replace.")
            case 1:
                self.dataManLineEdit1.setEnabled(True)
                self.dataManLineEdit2.setEnabled(False)
                self.dataManLineEdit1.setPlaceholderText("splitting text")
                self.dataManInstr.setText("Provide the splitter.")
            case 2:
                self.dataManLineEdit1.setEnabled(True)
                self.dataManLineEdit2.setEnabled(False)
                self.dataManLineEdit1.setPlaceholderText("index number")
                self.dataManInstr.setText("Only use this option after adding a split option.")
            case _:
                print("The index number is not working")
    
    def dataManCheckButton_method(self):
        self.man_response = self.response
        test_code = self.new_data_manipulation_code
        test_code = test_code.replace(f"{self.returning_variable_name}","self.man_response")
        exec(test_code)
        self.dataManCurrentResponse.setText(str(self.man_response))
        desired_data_index = self.desiredDataComboBox.currentIndex()
        match desired_data_index:
            case 0:
                try:
                    dummy = str(self.man_response)
                    self.desiredDataInstr.setText("Current response meets the requirement")
                except:
                    self.desiredDataInstr.setText("Current response doesn't meet the requirement")
            case 1:
                try:
                    dummy = int(self.man_response)
                    self.desiredDataInstr.setText("Current response meets the requirement")
                except:
                    self.desiredDataInstr.setText("Current response doesn't meet the requirement")
            case 2:
                try:
                    dummy = float(self.man_response)
                    self.desiredDataInstr.setText("Current response meets the requirement")
                except:
                    self.desiredDataInstr.setText("Current response doesn't meet the requirement")
        
    
    def dataManAddButton_method(self):
        index_number = self.dataManComboBox.currentIndex()
        match index_number:
            case 0:
                old_text = self.dataManLineEdit1.text()
                new_text = self.dataManLineEdit2.text()
                code_line = f'{self.returning_variable_name} = {self.returning_variable_name}.replace("{old_text}","{new_text}")\n'
                self.new_data_manipulation_code = self.new_data_manipulation_code + code_line
                self.dataManDisplay.setPlainText(self.new_data_manipulation_code)
            case 1:
                split_text = self.dataManLineEdit1.text()
                code_line = f'{self.returning_variable_name} = {self.returning_variable_name}.split("{split_text}")\n'
                self.new_data_manipulation_code = self.new_data_manipulation_code + code_line
                self.dataManDisplay.setPlainText(self.new_data_manipulation_code)
            case 2:
                try:
                    index = int(self.dataManLineEdit1.text())
                    code_line = f"{self.returning_variable_name} = {self.returning_variable_name}[{index}]\n"
                    self.new_data_manipulation_code = self.new_data_manipulation_code + code_line
                    self.dataManDisplay.setPlainText(self.new_data_manipulation_code)
                except:
                    self.dataManLineEdit1.setText("This index is invalid.")
            case _:
                print("The index number is not working")

    def dataManSave_method(self):
        try:
            with open(self.method_path, "r") as f:
                current_content = f.read()
                print(current_content)
                old_string = f'data_manipulation_code = \"\"\"{self.old_data_manipulation_code}\"\"\"'
                new_string = f'data_manipulation_code = \"\"\"{self.new_data_manipulation_code}\"\"\"'
                
                if old_string not in current_content:
                        print(f'"{old_string}" not found. No changes made.')
                        return

                new_content = current_content.replace(old_string, new_string)
                print(f'Successfully changed.')
            
            with open(self.method_path, "w") as f:    
                    f.write(new_content)
            
            self.old_data_manipulation_code = self.new_data_manipulation_code
        
        except FileNotFoundError:
            print(f"Error: The file '{self.method_path}' was not found.")

    def dataManDelete_method(self):
        self.new_data_manipulation_code = self.new_data_manipulation_code.split("\n")
        n = len(self.new_data_manipulation_code) - 2
        mid_function_code = ""
        for i  in range(0,n):
            mid_function_code = mid_function_code + self.new_data_manipulation_code[i] + "\n"
        
        self.new_data_manipulation_code = mid_function_code
        self.dataManDisplay.setPlainText(self.new_data_manipulation_code)
    
    def dataManClear_method(self):
        self.new_data_manipulation_code = ""
        self.dataManDisplay.setPlainText(self.new_data_manipulation_code)

    def dataManEdit_method(self):
        self.manualDataManEditWin = QMainWindow()
        self.manualDataManEditWid = meu.manual_edit_ui(self.new_data_manipulation_code)
        self.manualDataManEditWin.setCentralWidget(self.manualDataManEditWid)
        self.manualDataManEditWin.closeEvent = self.manualDataManEditWid.closeEvent
        
        self.manualDataManEditWin.setWindowTitle("Manually edit the data manipulation")
        self.manualDataManEditWin.resize(350, 350)
        self.manualDataManEditWin.move(500, 300)
        
        self.manualDataManEditWin.show()
        self.manualDataManEditWid.manualEditSave.clicked.connect(self.manual_edit_dataMan_save)
        self.manualDataManEditWid.manualEditCancel.clicked.connect(self.manualDataManEditWin.close)

    def manual_edit_dataMan_save(self):
        self.new_data_manipulation_code = self.manualDataManEditWid.code
        self.dataManDisplay.setPlainText(self.new_data_manipulation_code)
        self.manualDataManEditWin.close()
    
    def newCommandSaveButton_method(self):
        saving_function_code = ""
        saving_function_code_list = self.new_function_code.split("\n")
        
        data_manipulation_code_list = self.new_data_manipulation_code.split("\n")
        
# PUTTING THE FUNCTION AND DATA MANIPULATION TOGETHER
        last_code_line = saving_function_code_list.pop()
        saving_function_code_list.extend(data_manipulation_code_list)
        saving_function_code_list.append(last_code_line)
        n = len(saving_function_code_list)
        
        for i in range(0,n):
            saving_function_code = saving_function_code + "        " + saving_function_code_list[i] + "\n"
        
        for data_name, data_value in self.new_data_list.items():
            saving_function_code = saving_function_code.replace(f"{{{data_name}}}", data_value)

# ADD THE TEST FUNCTION
        try:
            with open(self.method_path, "a") as f:
                self.method_script = f"""
def {self.command_name}(self):
    try:
{saving_function_code}
    except Exception as e:
        print("Something went wrong: " + e)
"""
                print(self.method_script)
                f.write(self.method_script)     
        except FileNotFoundError:
            print(f"Error: The file '{self.method_path}' was not found.")
            
# EDIT THE ATTRIBUTE FILE
        # Import the newly made method file
        importing_line = f", {self.command_name}_method"
        try:
            with open(self.attribute_path, "r") as f:
                current_content = f.read()
                f.seek(0)
                current_content_list = f.readlines()
                print(current_content)
                old_string = current_content_list[2]
                old_string = old_string.replace("\n","")
                new_string = old_string + importing_line
                
                if old_string not in current_content:
                        print(f'"{old_string}" not found. No changes made.')
                        return

                new_content = current_content.replace(old_string, new_string)
                print(f'Successfully changed.')
            
            with open(self.attribute_path, "w") as f:    
                    f.write(new_content)
        
        except FileNotFoundError:
            print(f"Error: The file '{self.method_path}' was not found.")
            
        # Modify functions list
        ### Read the current functions list
        attribute_module = importlib.import_module(f"Tools.saved_instruments.Members.{self.instrument.model}.attributes")
        
        functions_dict = getattr(attribute_module, "functions")
        functions_dict[self.command_name] = f"{self.command_name}_method.{self.command_name}"
        functions_dict = "functions = " + str(functions_dict) + "\n"
        functions_dict = functions_dict.replace(f"'{self.command_name}_method.{self.command_name}'", f'{self.command_name}_method.{self.command_name}')
        
        
        try:
            with open(self.attribute_path, "r") as f:
                current_content_list = f.readlines()
                print(current_content_list)
                current_content_list[5] = functions_dict
                
                new_content = ""
                for i in range(0,len(current_content_list)):
                    new_content = new_content + current_content_list[i] 
                
                print(f'Successfully changed.')
            
            with open(self.attribute_path, "w") as f:    
                    f.write(new_content)
        
        except FileNotFoundError:
            print(f"Error: The file '{self.attribute_path}' was not found.")
            
        # Modify lists depending on the command type
        ### read command
        if self.command_type == 'READ':
            attribute_module = importlib.import_module(f"Tools.saved_instruments.Members.{self.instrument.model}.attributes")
        
            read_functions_dict = getattr(attribute_module, "read_functions")
            read_functions_dict[self.command_name] = f"{self.command_name}_method.{self.command_name}"
            read_functions_dict = "read_functions = " + str(read_functions_dict) + "\n"
            read_functions_dict = read_functions_dict.replace(f"'{self.command_name}_method.{self.command_name}'", f'{self.command_name}_method.{self.command_name}')
            
            try:
                with open(self.attribute_path, "r") as f:
                    current_content_list = f.readlines()
                    print(current_content_list)
                    current_content_list[6] = read_functions_dict
                    
                    new_content = ""
                    for i in range(0,len(current_content_list)):
                        new_content = new_content + current_content_list[i] 
                    
                    print(f'Successfully changed.')
                
                with open(self.attribute_path, "w") as f:    
                        f.write(new_content)
            except FileNotFoundError:
                print(f"Error: The file '{self.attribute_path}' was not found.")
        
        ### write command
        if self.command_type == 'WRITE':
            attribute_module = importlib.import_module(f"Tools.saved_instruments.Members.{self.instrument.model}.attributes")
        
            write_functions_dict = getattr(attribute_module, "write_functions")
            write_functions_dict[self.command_name] = f"{self.command_name}_method.{self.command_name}"
            write_functions_dict = "write_functions = " + str(write_functions_dict) + "\n"
            write_functions_dict = write_functions_dict.replace(f"'{self.command_name}_method.{self.command_name}'", f'{self.command_name}_method.{self.command_name}')
            
            try:
                with open(self.attribute_path, "r") as f:
                    current_content_list = f.readlines()
                    print(current_content_list)
                    current_content_list[7] = write_functions_dict
                    
                    new_content = ""
                    for i in range(0,len(current_content_list)):
                        new_content = new_content + current_content_list[i] 
                    
                    print(f'Successfully changed.')
                
                with open(self.attribute_path, "w") as f:    
                        f.write(new_content)
            except FileNotFoundError:
                print(f"Error: The file '{self.attribute_path}' was not found.")
            

        
            
        self.window.hide()
    
    def dataManSaveAsTemplate_method(self):
        pass

    def dataManImportTemplate_method(self):
        pass
    
    def newCommandCancelButton_method(self):
        self.closeEvent(QCloseEvent())
    
    def closeEvent(self, event:QCloseEvent):
        try:
            self.method_path.unlink()
        except:
            pass
        self.window.close()



class edit_command_setting_ui(QWidget):
    _GENERIC_NAME_RE = re.compile(r".*_\d+$")
    
    def __init__(self, instrument, interface, window, command_name):
        super().__init__()
        print("loadUi")
        uic.loadUi("GUI/ui_files/new_command.ui", self)
        
        self.instrument = instrument
        self.interface = str(interface)
        self.window = window
        
        self.comInterfaceLabel.setText(self.interface)
        self.original_command_name = command_name
        self.command_name = command_name
        self.method_module_path = f"Tools.saved_instruments.Members.{self.instrument.model}.{self.command_name}_method"
# CREATE A COPY FILE OF THE METHOD
        self.original_method_file = f"C:/Users/szkop/OneDrive/Desktop/YonKu/Tools/saved_instruments/Members/{self.instrument.model}/{self.command_name}_method.py"
        self.copy_method_file = f"C:/Users/szkop/OneDrive/Desktop/YonKu/Tools/saved_instruments/Members/{self.instrument.model}/{self.command_name}_method_copy.py"

        try:
            # Use shutil.copy2 to copy the file content and metadata (permissions, timestamps)
            shutil.copy2(self.original_method_file, self.copy_method_file)
            print(f"File copied.")
        except IOError as e:
            print(f"Error copying file: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        
        self.original_method_path = pathlib.Path(f"C:/Users/szkop/OneDrive/Desktop/YonKu/Tools/saved_instruments/Members/{self.instrument.model}/{self.command_name}_method_copy.py")
        self.method_path = pathlib.Path(f"C:/Users/szkop/OneDrive/Desktop/YonKu/Tools/saved_instruments/Members/{self.instrument.model}/{self.command_name}_method.py")

# CREATE A COPY FILE OF ATTRIBUTES
        self.original_attribute_file = f"C:/Users/szkop/OneDrive/Desktop/YonKu/Tools/saved_instruments/Members/{self.instrument.model}/attributes.py"
        self.copy_attribute_file = f"C:/Users/szkop/OneDrive/Desktop/YonKu/Tools/saved_instruments/Members/{self.instrument.model}/attributes_copy.py"

        try:
            # Use shutil.copy2 to copy the file content and metadata (permissions, timestamps)
            shutil.copy2(self.original_attribute_file, self.copy_attribute_file)
            print(f"File copied.")
        except IOError as e:
            print(f"Error copying file: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        
        self.original_attribute_path = pathlib.Path(f"C:/Users/szkop/OneDrive/Desktop/YonKu/Tools/saved_instruments/Members/{self.instrument.model}/attributes_copy.py")
        self.attribute_path = pathlib.Path(f"C:/Users/szkop/OneDrive/Desktop/YonKu/Tools/saved_instruments/Members/{self.instrument.model}/attributes.py")

# GET RID OF THE EXISTING FUNCTION
        try:
            with open(self.method_path, "r") as f:
                current_content_list = f.readlines()
                function_start_sign = f"def {self.command_name}(self):\n"
                new_content = ""
                
                for i in range(0,len(current_content_list)):
                    if current_content_list[i] == function_start_sign:
                        break
                    else:
                        new_content = new_content + current_content_list[i]
            
            with open(self.method_path, "w") as f:    
                    f.write(new_content)
        
        except FileNotFoundError:
            print(f"Error: The file '{self.method_path}' was not found.")

# ATTRIBUTES ASSIGNMENT
        try:
            self.method_module = importlib.import_module(self.method_module_path)
            self.command_name = getattr(self.method_module, "command_name")
            self.command_text = getattr(self.method_module, "command_text")
            
            self.old_data_list = getattr(self.method_module, "data_list")
            self.new_data_list = getattr(self.method_module, "data_list")
                   
            self.old_test_data_list = getattr(self.method_module, "data_list")
            self.new_test_data_list = getattr(self.method_module, "data_list")
            
            self.command_type = getattr(self.method_module, "command_type")
            self.communication_syntax = getattr(self.method_module, "communication_syntax")
            self.desired_data_type = getattr(self.method_module, "desired_data_type")
            
            self.old_function_code = getattr(self.method_module, "function_code")
            self.new_function_code = getattr(self.method_module, "function_code")
            
            self.old_data_manipulation_code = getattr(self.method_module, "data_manipulation_code")
            self.new_data_manipulation_code = getattr(self.method_module, "data_manipulation_code")
            
            self.nameLineEdit.setText(self.command_name)
            self.commandText.setText(self.command_text)
            
            for data_name, default_value in self.old_data_list.items():
                self.dataComboBox.addItem(data_name)
                self.testComboBox.addItem(data_name)
            if self.old_data_list:
                self.dataDefaultValue.setText(self.old_data_list[self.dataComboBox.currentText()])
                self.testValue.setText(self.old_data_list[self.testComboBox.currentText()])
            
            match self.command_type:
                case 'READ':
                    self.commandTypeComboBox.setCurrentIndex(0)
                case 'WRITE':
                    self.commandTypeComboBox.setCurrentIndex(1)
            
            match self.communication_syntax:
                case 'ASCII':
                    self.comSystemComboBox.setCurrentIndex(0)
                case 'Binary':
                    self.comSystemComboBox.setCurrentIndex(1)
                    
            match self.desired_data_type:
                case 'string':
                    self.desiredDataComboBox.setCurrentIndex(0)
                case 'integer':
                    self.desiredDataComboBox.setCurrentIndex(1)
                case 'float':
                    self.desiredDataComboBox.setCurrentIndex(2)
                    
            self.functionDisplay.setPlainText(self.old_function_code)
            self.dataManDisplay.setPlainText(self.old_data_manipulation_code)
            
            
            self.writeCommandCheckBox.stateChanged.connect(self.writeCommandCheckBox_method)
            self.queryCommandCheckBox.stateChanged.connect(self.queryCommandCheckBox_method)
            self.dataComboBox.currentIndexChanged.connect(self.change_data_default)
            self.testComboBox.currentIndexChanged.connect(self.change_test_data_default)
            self.dataManComboBox.currentIndexChanged.connect(self.change_data_man_line_setting)
            
            self.method_script = ""
            self.response = ""
            self.man_response = ""
            self.returning_variable_name = "response"

            self.desiredDataInstr.setText("")
            
        except Exception as e:
            print(f"Error: {e}")
            
        self._connect_pushbuttons()
    
        
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
        try:
            with open(self.method_path, "r") as f:
                current_content = f.read()
                print(current_content)
                old_string = f'command_text = "{self.command_text}"'
                new_string = f'command_text = "{self.commandText.text()}"'
                
                if old_string not in current_content:
                        print(f'"{old_string}" not found. No changes made.')
                        return

                new_content = current_content.replace(old_string, new_string)
                print(f'Successfully changed "{old_string}" to "{new_string}".')
            
            with open(self.method_path, "w") as f:    
                    f.write(new_content)
            
            self.command_text = self.commandText.text()
        
        except FileNotFoundError:
            print(f"Error: The file '{self.method_path}' was not found.")
        
    # -------------------------------
    # Data type buttons
    # -------------------------------
    def dataAddButton_method(self):
        data_name = "Data" + str(self.dataComboBox.count())
        self.dataComboBox.addItem(data_name)
        self.testComboBox.addItem(data_name)
        self.new_data_list[data_name] = ""
        self.new_test_data_list[data_name] = ""
        try:
            with open(self.method_path, "r") as f:
                current_content = f.read()
                print(current_content)
                old_string = f'data_list = {self.old_data_list}'
                new_string = f'data_list = {self.new_data_list}'
                
                if old_string not in current_content:
                        print(f'"{old_string}" not found. No changes made.')
                        return

                new_content = current_content.replace(old_string, new_string)
                print(f'Successfully changed "{old_string}" to "{new_string}".')
            
            with open(self.method_path, "w") as f:    
                    f.write(new_content)
            
            self.old_data_list = self.new_data_list
        
        except FileNotFoundError:
            print(f"Error: The file '{self.method_path}' was not found.")

    def dataSaveButton_method(self):
        data_name = self.dataComboBox.currentText()
        self.new_data_list[data_name] = self.dataDefaultValue.text()
        self.new_test_data_list[data_name] = self.dataDefaultValue.text()
        try:
            with open(self.method_path, "r") as f:
                current_content = f.read()
                print(current_content)
                old_string = f'data_list = {self.old_data_list}'
                new_string = f'data_list = {self.new_data_list}'
                
                if old_string not in current_content:
                        print(f'"{old_string}" not found. No changes made.')
                        return

                new_content = current_content.replace(old_string, new_string)
                print(f'Successfully changed "{old_string}" to "{new_string}".')
            
            with open(self.method_path, "w") as f:    
                    f.write(new_content)
            
            self.old_data_list = self.new_data_list
        
        except FileNotFoundError:
            print(f"Error: The file '{self.method_path}' was not found.")
    
    def change_data_default(self):
        self.dataDefaultValue.setText(self.old_data_list[self.dataComboBox.currentText()])

    def dataRemoveButton_method(self):
        data_name = self.dataComboBox.currentText()
        self.dataComboBox.removeItem(self.dataComboBox.currentIndex())
        self.testComboBox.removeItem(self.dataComboBox.currentIndex())
        del self.new_data_list[data_name]
        try:
            with open(self.method_path, "r") as f:
                current_content = f.read()
                print(current_content)
                old_string = f'data_list = {self.old_data_list}'
                new_string = f'data_list = {self.new_data_list}'
                
                if old_string not in current_content:
                        print(f'"{old_string}" not found. No changes made.')
                        return

                new_content = current_content.replace(old_string, new_string)
                print(f'Successfully changed "{old_string}" to "{new_string}".')
            
            with open(self.method_path, "w") as f:    
                    f.write(new_content)
            
            self.old_data_list = self.new_data_list
        
        except FileNotFoundError:
            print(f"Error: The file '{self.method_path}' was not found.")
    
    def commandTypeSaveButton_method(self):
        try:
            with open(self.method_path, "r") as f:
                current_content = f.read()
                print(current_content)
                old_string = f'command_type = "{self.command_type}"'
                new_string = f'command_type = "{self.commandTypeComboBox.currentText()}"'
                
                if old_string not in current_content:
                        print(f'"{old_string}" not found. No changes made.')
                        return

                new_content = current_content.replace(old_string, new_string)
                print(f'Successfully changed "{old_string}" to "{new_string}".')
            
            with open(self.method_path, "w") as f:    
                    f.write(new_content)
            
            self.command_type = self.commandTypeComboBox.currentText()
        
        except FileNotFoundError:
            print(f"Error: The file '{self.method_path}' was not found.")

    # -------------------------------
    # BUILD YOUR FUNCTION
    # -------------------------------
    
    def comSystemSaveButton_method(self):
        try:
            with open(self.method_path, "r") as f:
                current_content = f.read()
                print(current_content)
                old_string = f'communication_syntax = "{self.communication_syntax}"'
                new_string = f'communication_syntax = "{self.comSystemComboBox.currentText()}"'
                
                if old_string not in current_content:
                        print(f'"{old_string}" not found. No changes made.')
                        return

                new_content = current_content.replace(old_string, new_string)
                print(f'Successfully changed "{old_string}" to "{new_string}".')
            
            with open(self.method_path, "w") as f:    
                    f.write(new_content)
            
            self.command_text = self.commandTypeComboBox.currentText()
        
        except FileNotFoundError:
            print(f"Error: The file '{self.method_path}' was not found.")
    
    def writeCommandCheckBox_method(self):
        if self.writeCommandCheckBox.isChecked():
            self.writeLineEdit.setText(self.command_text)
            self.writeLineEdit.setEnabled(False)
        else:
            self.writeLineEdit.setEnabled(True)
        
        
    def writeAddButton_method(self):
        code_line = 'self.write("' + self.writeLineEdit.text() + '")\n'
        self.new_function_code = self.new_function_code + code_line
        self.functionDisplay.setPlainText(self.new_function_code)
        
        

    def readAddButton_method(self):
        variable_name = self.readVariableLineEdit.text()
        code_line = f'{variable_name} = self.read()\n'
        self.new_function_code = self.new_function_code + code_line
        self.functionDisplay.setPlainText(self.new_function_code)

    def queryAddButton_method(self):
        variable_name = self.queryVariableLineEdit.text()
        code_line = f'{variable_name} = self.query("' + self.queryCommandLineEdit.text() + '")\n'
        self.new_function_code = self.new_function_code + code_line
        self.functionDisplay.setPlainText(self.new_function_code)
        
    def queryCommandCheckBox_method(self):
        if self.queryCommandCheckBox.isChecked():
            self.queryCommandLineEdit.setText(self.command_text)
            self.queryCommandLineEdit.setEnabled(False)
        else:
            self.queryCommandLineEdit.setEnabled(True)
        
    def sleepAddButton_method(self):
        sleep_period = self.sleepLineEdit.text()
        try:
            sleep_period = int(sleep_period)
        except:
            self.sleepLineEdit.setText("This period is invalid. The period has to be an integer in seconds.")
        code_line = f'time.sleep({sleep_period})\n'
        self.new_function_code = self.new_function_code + code_line
        self.functionDisplay.setPlainText(self.new_function_code)
    
    def returnAddButton_method(self):
        self.returning_variable_name = self.returnLineEdit.text()
        code_line = f"return {self.returning_variable_name}"
        self.new_function_code = self.new_function_code + code_line
        self.functionDisplay.setPlainText(self.new_function_code)
        

    # -------------------------------
    # Function builder buttons
    # -------------------------------
    def functionDelete_method(self):
        self.new_function_code = self.new_function_code.split("\n")
        n = len(self.new_function_code) - 2
        mid_function_code = ""
        for i  in range(0,n):
            mid_function_code = mid_function_code + self.new_function_code[i] + "\n"
        
        self.new_function_code = mid_function_code
        self.functionDisplay.setPlainText(self.new_function_code)

    def functionClear_method(self):
        self.new_function_code = ""
        self.functionDisplay.setPlainText(self.new_function_code)
        

    def functionEdit_method(self):
        self.manualEditWin = QMainWindow()
        self.manualEditWid = meu.manual_edit_ui(self.new_function_code)
        self.manualEditWin.setCentralWidget(self.manualEditWid)
        self.manualEditWin.closeEvent = self.manualEditWid.closeEvent
        
        self.manualEditWin.setWindowTitle("Manually edit the function")
        self.manualEditWin.resize(350, 350)
        self.manualEditWin.move(500, 300)
        
        self.manualEditWin.show()
        self.manualEditWid.manualEditSave.clicked.connect(self.manual_edit_save)
        self.manualEditWid.manualEditCancel.clicked.connect(self.manualEditWin.close)
    
    def manual_edit_save(self):
        self.new_function_code = self.manualEditWid.code
        self.functionDisplay.setPlainText(self.new_function_code)
        self.manualEditWin.close()
    
        
    def functionSave_method(self):
        try:
            with open(self.method_path, "r") as f:
                current_content = f.read()
                print(current_content)
                old_string = f'function_code = \"\"\"{self.old_function_code}\"\"\"'
                new_string = f'function_code = \"\"\"{self.new_function_code}\"\"\"'
                
                if old_string not in current_content:
                        print(f'"{old_string}" not found. No changes made.')
                        return

                new_content = current_content.replace(old_string, new_string)
                print(f'Successfully changed.')
            
            with open(self.method_path, "w") as f:    
                    f.write(new_content)
            
            self.old_function_code = self.new_function_code
        
        except FileNotFoundError:
            print(f"Error: The file '{self.method_path}' was not found.")

    def functionSaveAsTemplate_method(self):
        pass

    def functionImportTemplate_method(self):
        pass

    # -------------------------------
    # Test section buttons
    # -------------------------------
    def testSave_method(self):
        data_name = self.self.testComboBox.currentText()
        self.new_test_data_list[data_name] = self.testValue.text()
    
    def change_test_data_default(self):
        self.testValue.setText(self.new_test_data_list[self.testComboBox.currentText()])

    def testExecute_method(self):
        function_code = ""
        function_code_list = self.new_function_code.split("\n")
        n = len(function_code_list)
        
        for i in range(0,n):
            function_code = function_code + "        " + function_code_list[i] + "\n"
        
        for data_name, data_value in self.new_test_data_list.items():
            function_code = function_code.replace(f"{{{data_name}}}", data_value)

# ADD THE TEST FUNCTION
        try:
            with open(self.method_path, "a") as f:
                self.method_script = f"""
def {self.command_name}(self):
    try:
{function_code}
    except Exception as e:
        print("Something went wrong: " + e)
"""
                print(self.method_script)
                f.write(self.method_script)     
        except FileNotFoundError:
            print(f"Error: The file '{self.method_path}' was not found.")
# IMPORT AND RUN THE TEST FUNCTION
        try:
            module_path = f"Tools.saved_instruments.Members.{self.instrument.model}.{self.command_name}_method"
            if module_path in sys.modules:
                method_module = importlib.reload(sys.modules[module_path])
            else:
                method_module = importlib.import_module(module_path)
            # 2. Get the specific function/attribute from the module using getattr
            method_function = getattr(method_module, f"{self.command_name}")
            
            self.response = method_function(self.instrument)
            print("This is the respone: " + self.response)
            
            
            
            self.testResponse.setText(self.response)

        except (ImportError, AttributeError) as e:
            print(f"Error: {e}")
        except IndentationError:
            self.testResponse.setText("The function code is empty.")
        except Exception as e:
                self.testResponse.setText(str(e))
                print(str(e))
        
            
# REMOVE THE TEST FUNCTION
        try:
            with open(self.method_path, "r") as f:
                current_content = f.read()
                old_string = self.method_script
                new_string = ""
                
                if old_string not in current_content:
                        print(f'"{old_string}" not found. No changes made.')
                        return

                new_content = current_content.replace(old_string, new_string)
                print(f'Successfully changed.')
            
            with open(self.method_path, "w") as f:    
                    f.write(new_content)
        
        except FileNotFoundError:
            print(f"Error: The file '{self.method_path}' was not found.")
            

    # -------------------------------
    # Data manipulation buttons
    # -------------------------------
    # def dataManCheckButton_method(self):
    #     self.man_response = self.response
    
    def change_data_man_line_setting(self):
        index_number = self.dataManComboBox.currentIndex()
        match index_number:
            case 0:
                self.dataManLineEdit1.setEnabled(True)
                self.dataManLineEdit2.setEnabled(True)
                self.dataManLineEdit1.setPlaceholderText("from")
                self.dataManLineEdit2.setPlaceholderText("to")
                self.dataManInstr.setText("Provide the old and new texts to replace.")
            case 1:
                self.dataManLineEdit1.setEnabled(True)
                self.dataManLineEdit2.setEnabled(False)
                self.dataManLineEdit1.setPlaceholderText("splitting text")
                self.dataManInstr.setText("Provide the splitter.")
            case 2:
                self.dataManLineEdit1.setEnabled(True)
                self.dataManLineEdit2.setEnabled(False)
                self.dataManLineEdit1.setPlaceholderText("index number")
                self.dataManInstr.setText("Only use this option after adding a split option.")
            case _:
                print("The index number is not working")
    
    def dataManCheckButton_method(self):
        self.man_response = self.response
        test_code = self.new_data_manipulation_code
        test_code = test_code.replace(f"{self.returning_variable_name}","self.man_response")
        exec(test_code)
        self.dataManCurrentResponse.setText(str(self.man_response))
        desired_data_index = self.desiredDataComboBox.currentIndex()
        match desired_data_index:
            case 0:
                try:
                    dummy = str(self.man_response)
                    self.desiredDataInstr.setText("Current response meets the requirement")
                except:
                    self.desiredDataInstr.setText("Current response doesn't meet the requirement")
            case 1:
                try:
                    dummy = int(self.man_response)
                    self.desiredDataInstr.setText("Current response meets the requirement")
                except:
                    self.desiredDataInstr.setText("Current response doesn't meet the requirement")
            case 2:
                try:
                    dummy = float(self.man_response)
                    self.desiredDataInstr.setText("Current response meets the requirement")
                except:
                    self.desiredDataInstr.setText("Current response doesn't meet the requirement")
        
    
    def dataManAddButton_method(self):
        index_number = self.dataManComboBox.currentIndex()
        match index_number:
            case 0:
                old_text = self.dataManLineEdit1.text()
                new_text = self.dataManLineEdit2.text()
                code_line = f'{self.returning_variable_name} = {self.returning_variable_name}.replace("{old_text}","{new_text}")\n'
                self.new_data_manipulation_code = self.new_data_manipulation_code + code_line
                self.dataManDisplay.setPlainText(self.new_data_manipulation_code)
            case 1:
                split_text = self.dataManLineEdit1.text()
                code_line = f'{self.returning_variable_name} = {self.returning_variable_name}.split("{split_text}")\n'
                self.new_data_manipulation_code = self.new_data_manipulation_code + code_line
                self.dataManDisplay.setPlainText(self.new_data_manipulation_code)
            case 2:
                try:
                    index = int(self.dataManLineEdit1.text())
                    code_line = f"{self.returning_variable_name} = {self.returning_variable_name}[{index}]\n"
                    self.new_data_manipulation_code = self.new_data_manipulation_code + code_line
                    self.dataManDisplay.setPlainText(self.new_data_manipulation_code)
                except:
                    self.dataManLineEdit1.setText("This index is invalid.")
            case _:
                print("The index number is not working")

    def dataManSave_method(self):
        try:
            with open(self.method_path, "r") as f:
                current_content = f.read()
                print(current_content)
                old_string = f'data_manipulation_code = \"\"\"{self.old_data_manipulation_code}\"\"\"'
                new_string = f'data_manipulation_code = \"\"\"{self.new_data_manipulation_code}\"\"\"'
                
                if old_string not in current_content:
                        print(f'"{old_string}" not found. No changes made.')
                        return

                new_content = current_content.replace(old_string, new_string)
                print(f'Successfully changed.')
            
            with open(self.method_path, "w") as f:    
                    f.write(new_content)
            
            self.old_data_manipulation_code = self.new_data_manipulation_code
        
        except FileNotFoundError:
            print(f"Error: The file '{self.method_path}' was not found.")

    def dataManDelete_method(self):
        self.new_data_manipulation_code = self.new_data_manipulation_code.split("\n")
        n = len(self.new_data_manipulation_code) - 2
        mid_function_code = ""
        for i  in range(0,n):
            mid_function_code = mid_function_code + self.new_data_manipulation_code[i] + "\n"
        
        self.new_data_manipulation_code = mid_function_code
        self.dataManDisplay.setPlainText(self.new_data_manipulation_code)
    
    def dataManClear_method(self):
        self.new_data_manipulation_code = ""
        self.dataManDisplay.setPlainText(self.new_data_manipulation_code)

    def dataManEdit_method(self):
        self.manualDataManEditWin = QMainWindow()
        self.manualDataManEditWid = meu.manual_edit_ui(self.new_data_manipulation_code)
        self.manualDataManEditWin.setCentralWidget(self.manualDataManEditWid)
        self.manualDataManEditWin.closeEvent = self.manualDataManEditWid.closeEvent
        
        self.manualDataManEditWin.setWindowTitle("Manually edit the data manipulation")
        self.manualDataManEditWin.resize(350, 350)
        self.manualDataManEditWin.move(500, 300)
        
        self.manualDataManEditWin.show()
        self.manualDataManEditWid.manualEditSave.clicked.connect(self.manual_edit_dataMan_save)
        self.manualDataManEditWid.manualEditCancel.clicked.connect(self.manualDataManEditWin.close)

    def manual_edit_dataMan_save(self):
        self.new_data_manipulation_code = self.manualDataManEditWid.code
        self.dataManDisplay.setPlainText(self.new_data_manipulation_code)
        self.manualDataManEditWin.close()
    
    def newCommandSaveButton_method(self):
        saving_function_code = ""
        saving_function_code_list = self.new_function_code.split("\n")
        
        data_manipulation_code_list = self.new_data_manipulation_code.split("\n")
        
# PUTTING THE FUNCTION AND DATA MANIPULATION TOGETHER
        last_code_line = saving_function_code_list.pop()
        saving_function_code_list.extend(data_manipulation_code_list)
        saving_function_code_list.append(last_code_line)
        n = len(saving_function_code_list)
        
        for i in range(0,n):
            saving_function_code = saving_function_code + "        " + saving_function_code_list[i] + "\n"
        
        for data_name, data_value in self.new_data_list.items():
            saving_function_code = saving_function_code.replace(f"{{{data_name}}}", data_value)

# ADD THE TEST FUNCTION
        try:
            with open(self.method_path, "a") as f:
                self.method_script = f"""
def {self.command_name}(self):
    try:
{saving_function_code}
    except Exception as e:
        print("Something went wrong: " + e)
"""
                print(self.method_script)
                f.write(self.method_script)     
        except FileNotFoundError:
            print(f"Error: The file '{self.method_path}' was not found.")
            
# EDIT THE ATTRIBUTE FILE
        # Import the newly made method file
        importing_line = f", {self.command_name}_method"
        try:
            with open(self.attribute_path, "r") as f:
                current_content = f.read()
                f.seek(0)
                current_content_list = f.readlines()
                print(current_content)
                old_string = current_content_list[2]
                old_string = old_string.replace("\n","")
                new_string = old_string.replace(f", {self.original_command_name}_method", f", {self.original_command_name}_method{importing_line}")
                
                if old_string not in current_content:
                        print(f'"{old_string}" not found. No changes made.')
                        return

                new_content = current_content.replace(old_string, new_string)
                
                print(f'Successfully changed.')
            
            with open(self.attribute_path, "w") as f:    
                    f.write(new_content)
        
        except FileNotFoundError:
            print(f"Error: The file '{self.method_path}' was not found.")
            
        # Modify functions list
        ### GET RID OF THE ORIGINAL FUNCTIONS AND REPLACE FUNCTION LIST
        attribute_module = importlib.import_module(f"Tools.saved_instruments.Members.{self.instrument.model}.attributes")
        
        functions_dict = getattr(attribute_module, "functions")
        try:
            del functions_dict[self.original_command_name]
            functions_dict[self.command_name] = f"{self.command_name}_method.{self.command_name}"
        except KeyError:
            pass
        functions_dict = "functions = " + str(read_functions_dict) + "\n"
        functions_dict = functions_dict.replace(f"'{self.command_name}_method.{self.command_name}'", f"{self.command_name}_method.{self.command_name}")
        
        read_functions_dict = getattr(attribute_module, "read_functions")
        try:
            del read_functions_dict[self.original_command_name]
        except KeyError:
            pass
        read_functions_dict = "read_functions = " + str(read_functions_dict) + "\n"
        
        write_functions_dict = getattr(attribute_module, "write_functions")
        try:
            del write_functions_dict[self.original_command_name]
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
        
        # Add the edited function to functions list
            
        # Modify lists depending on the command type
        ### read command
        if self.command_type == 'READ':
            attribute_module = importlib.import_module(f"Tools.saved_instruments.Members.{self.instrument.model}.attributes")
        
            read_functions_dict = getattr(attribute_module, "read_functions")
            read_functions_dict[self.command_name] = f"{self.command_name}_method.{self.command_name}"
            read_functions_dict = "read_functions = " + str(read_functions_dict) + "\n"
            read_functions_dict = read_functions_dict.replace(f"'{self.command_name}_method.{self.command_name}'", f'{self.command_name}_method.{self.command_name}')
            
            try:
                with open(self.attribute_path, "r") as f:
                    current_content_list = f.readlines()
                    print(current_content_list)
                    current_content_list[6] = read_functions_dict
                    
                    new_content = ""
                    for i in range(0,len(current_content_list)):
                        new_content = new_content + current_content_list[i] 
                    
                    print(f'Successfully changed.')
                
                with open(self.attribute_path, "w") as f:    
                        f.write(new_content)
            except FileNotFoundError:
                print(f"Error: The file '{self.attribute_path}' was not found.")
        
        ### write command
        if self.command_type == 'WRITE':
            attribute_module = importlib.import_module(f"Tools.saved_instruments.Members.{self.instrument.model}.attributes")
        
            write_functions_dict = getattr(attribute_module, "write_functions")
            write_functions_dict[self.command_name] = f"{self.command_name}_method.{self.command_name}"
            write_functions_dict = "write_functions = " + str(write_functions_dict) + "\n"
            write_functions_dict = write_functions_dict.replace(f"'{self.command_name}_method.{self.command_name}'", f'{self.command_name}_method.{self.command_name}')
            
            try:
                with open(self.attribute_path, "r") as f:
                    current_content_list = f.readlines()
                    print(current_content_list)
                    current_content_list[7] = write_functions_dict
                    
                    new_content = ""
                    for i in range(0,len(current_content_list)):
                        new_content = new_content + current_content_list[i] 
                    
                    print(f'Successfully changed.')
                
                with open(self.attribute_path, "w") as f:    
                        f.write(new_content)
            except FileNotFoundError:
                print(f"Error: The file '{self.attribute_path}' was not found.")

# get the right imports back(getting rid of copy)
        actual_importing_line = f", {self.command_name}_method"
        try:
            with open(self.attribute_path, "r") as f:
                current_content = f.read()
                f.seek(0)
                current_content_list = f.readlines()
                print(current_content)
                old_string = current_content_list[2]
                old_string = old_string.replace("\n","")
                new_string = old_string.replace(importing_line, actual_importing_line)
                
                if old_string not in current_content:
                        print(f'"{old_string}" not found. No changes made.')
                        return

                new_content = current_content.replace(old_string, new_string)
                print(f'Successfully changed.')
            
            with open(self.attribute_path, "w") as f:    
                    f.write(new_content)
        
        except FileNotFoundError:
            print(f"Error: The file '{self.method_path}' was not found.")
        
#delete the original file
        self.original_method_path.unlink()
        self.original_attribute_path.unlink()
            
        self.window.hide()
    
    def dataManSaveAsTemplate_method(self):
        pass

    def dataManImportTemplate_method(self):
        pass
    
    def newCommandCancelButton_method(self):
        self.closeEvent(QCloseEvent())
    
    def closeEvent(self, event:QCloseEvent):
        try:
            self.method_path.unlink()
            self.attribute_path.unlink()
            new_method_path = pathlib.Path(f"C:/Users/szkop/OneDrive/Desktop/YonKu/Tools/saved_instruments/Members/{self.instrument.model}/{self.original_command_name}_method.py")
            new_attribute_path = pathlib.Path(f"C:/Users/szkop/OneDrive/Desktop/YonKu/Tools/saved_instruments/Members/{self.instrument.model}/attributes.py")
            try:
                self.original_method_path.rename(new_method_path)
                self.original_attribute_path.rename(new_attribute_path)
            except FileNotFoundError:
                print(f"Error: The file '{self.attribute_path}' was not found.")  
        except:
            pass
        self.window.close()

        