from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget, QComboBox, QHBoxLayout, QLineEdit, QMessageBox
from PyQt5.QtGui import QCloseEvent
from PyQt5 import uic
import sys
import re
import types
import pathlib
import importlib
import shutil
import os
import json
import ast
import builtins

from GUI import ManualEditUi as meu

from project_paths import GUI_DIR, SAVED_INSTRUMENTS_DIR, INSTRUMENT_CONTROL_UIS_DIR, INSTRUMENT_WIDGETS_DIR


class new_command_setting_ui(QWidget):
    _GENERIC_NAME_RE = re.compile(r".*_\d+$")
    
    def __init__(self, instrument, interface, window):
        super().__init__()
        print("loadUi")
        uic.loadUi(f"{GUI_DIR}/ui_files/new_command.ui", self)
        
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
        self.parameterComboBox.currentIndexChanged.connect(self.change_data_default)
        self.testComboBox.currentIndexChanged.connect(self.change_test_data_default)
        self.dataManComboBox.currentIndexChanged.connect(self.change_data_man_line_setting)
        
        self.method_script = ""
        self.response = ""
        self.man_response = ""
        self.returning_variable_name = "response"

        self.desiredDataInstr.setText("")
        
        self.create_member_folder()
        self._initialize_returned_data_section()
        self._connect_pushbuttons()
    
    def create_member_folder(self):
        
        print("creating folders")
        instrument_folder = SAVED_INSTRUMENTS_DIR / self.instrument.model
        methods_folder = instrument_folder / "methods"

        instrument_folder.mkdir(parents=True, exist_ok=True)
        methods_folder.mkdir(parents=True, exist_ok=True)

        self.methods_folder = methods_folder
        self.attribute_path = instrument_folder / "attributes.py"
        self.metadata_path = instrument_folder / "metadata.json"

        self.method_path = None
        self.test_method_path = self.methods_folder / "__draft_test__.py"
        
        # self.method_name = "temporary_command"
        # index = self.try_make_method_file(self.method_name, 0)
        # self.method_name = f"{self.method_name}_{index}"
        
        
#         with open(self.method_path, "w") as f:
#             script = f"""
# command_name = "{self.command_name}"
# command_text = "{self.command_text}"
# data_list = {self.old_data_list}
# command_type = "{self.command_type}"
# communication_syntax = "{self.communication_syntax}"
# desired_data_type = "{self.desiredparameterComboBox.currentText()}"

# function_code = \"\"\"{self.old_function_code}\"\"\"
# data_manipulation_code = \"\"\"{self.old_data_manipulation_code}\"\"\"
# """
#             f.write(script)
#             f.close()
        
        
        
        
    def try_make_method_file(self, method_name, num):
        method_real_name = method_name + "_" + str(num)
        method_path = SAVED_INSTRUMENTS_DIR / self.instrument.model / "methods" / f"{method_real_name}.py"
        if method_path.exists():
            return self.try_make_method_file(method_name, num + 1)
        method_path.touch()
        return num

    def load_metadata(self):
        if not self.metadata_path.exists():
            return {
                "data_type": {},
                "data_label": {},
                "data_unit": {},
                "value_format": {},
                "initial_state": {},
                "methods": {}
            }

        with open(self.metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def save_metadata(self, metadata):
        with open(self.metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=4) 

    def update_metadata_for_command(self):
        metadata = self.load_metadata()

        metadata.setdefault("data_type", {})
        metadata.setdefault("data_label", {})
        metadata.setdefault("data_unit", {})
        metadata.setdefault("value_format", {})
        metadata.setdefault("initial_state", {})
        metadata.setdefault("methods", {})

        command_name = self.command_name
        linked_data = self._returned_data_metadata(metadata)

        metadata["methods"][command_name] = {
            "module": command_name,
            "function": "run",
            "command_type": self.command_type,
            "command_text": self.command_text,
            "communication_syntax": self.communication_syntax,
            "desired_data_type": self.desiredDataComboBox.currentText(),
            "command_linked_data": linked_data
        }

        self.save_metadata(metadata)

    def _initialize_returned_data_section(self):
        """Configure optional, new-only data-function output metadata."""
        self.associateReturnedDataCheckBox.toggled.connect(
            self._update_returned_data_controls
        )
        self.returnedDataChannelCountSpinBox.valueChanged.connect(
            self._build_returned_data_channel_fields
        )
        self.commandTypeComboBox.currentTextChanged.connect(
            self._update_returned_data_visibility
        )
        self.returnedDataChannelCountSpinBox.setMinimum(1)
        self.returnedDataChannelCountSpinBox.setMaximum(64)
        self.returnedDataChannelCountSpinBox.setValue(1)
        self._build_returned_data_channel_fields()
        self._update_returned_data_visibility(self.commandTypeComboBox.currentText())

    def _update_returned_data_visibility(self, command_type):
        is_read_command = command_type.upper() == "READ"
        self.returnedDataFrame.setVisible(is_read_command)
        self.associateReturnedDataCheckBox.setEnabled(is_read_command)
        self._update_returned_data_controls(
            is_read_command and self.associateReturnedDataCheckBox.isChecked()
        )

    def _update_returned_data_controls(self, enabled):
        enabled = bool(enabled) and self.commandTypeComboBox.currentText().upper() == "READ"
        self.dataTypeIdLineEdit.setEnabled(enabled)
        self.returnedDataChannelCountSpinBox.setEnabled(enabled)
        self.returnedDataChannelsFrame.setEnabled(enabled)
        self.desiredDataComboBox.setEnabled(not enabled)
        if enabled:
            self.desiredDataInstr.setText(
                "Returned data must be a list matching the configured channels and formats."
            )
        else:
            self.desiredDataInstr.setText("")

    def _build_returned_data_channel_fields(self):
        while self.returnedDataChannelsLayout.count():
            item = self.returnedDataChannelsLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

        self.returned_data_channel_fields = []
        for index in range(self.returnedDataChannelCountSpinBox.value()):
            row = QHBoxLayout()
            channel_id = QLineEdit(f"ch_{chr(ord('A') + index)}" if index < 26 else f"ch_{index + 1}")
            label = QLineEdit()
            unit = QLineEdit()
            value_format = QComboBox()
            value_format.addItems(["Float", "Integer", "Text", "Boolean"])
            row.addWidget(QLabel(f"Channel {index + 1}:"))
            row.addWidget(channel_id)
            row.addWidget(QLabel("Label:"))
            row.addWidget(label)
            row.addWidget(QLabel("Unit:"))
            row.addWidget(unit)
            row.addWidget(QLabel("Format:"))
            row.addWidget(value_format)
            self.returnedDataChannelsLayout.addLayout(row)
            self.returned_data_channel_fields.append(
                (channel_id, label, unit, value_format)
            )

    def _returned_data_metadata(self, metadata):
        """Return command link metadata and add a newly defined type when needed."""
        if self.command_type.upper() != "READ":
            return {"data_function": False, "data_type": None}

        if not self.associateReturnedDataCheckBox.isChecked():
            return {"data_function": False, "data_type": None}

        data_type_id = self.dataTypeIdLineEdit.text().strip()
        if not data_type_id.isidentifier():
            raise ValueError("Returned Data Type ID must be a valid Python identifier.")
        if data_type_id in metadata["data_type"]:
            raise ValueError(f"Returned data type '{data_type_id}' already exists.")

        channels = []
        labels = {}
        units = {}
        formats = {}
        for channel_id, label, unit, value_format in self.returned_data_channel_fields:
            channel = channel_id.text().strip()
            if not channel.isidentifier():
                raise ValueError("Each Returned Data channel ID must be a valid Python identifier.")
            if channel in channels:
                raise ValueError("Returned Data channel IDs must be unique.")
            channels.append(channel)
            labels[channel] = label.text().strip() or channel
            units[channel] = unit.text().strip()
            formats[channel] = value_format.currentText().lower()

        metadata["data_type"][data_type_id] = channels
        metadata["data_label"][data_type_id] = labels
        metadata["data_unit"][data_type_id] = units
        metadata["value_format"][data_type_id] = formats
        return {"data_function": True, "data_type": data_type_id}

    def _validate_returned_data_selection(self):
        """Validate output data before creating the command module."""
        self._returned_data_metadata(self.load_metadata())

    def _returned_data_validation_code(self, return_line):
        """Convert a final return expression into a validated channel-value list."""
        if not self.associateReturnedDataCheckBox.isChecked():
            return [return_line]

        return_line = return_line.strip()
        if not return_line.startswith("return "):
            raise ValueError(
                "A data-function READ command must end with 'return <value>'."
            )

        formats = [
            value_format.currentText().lower()
            for _, _, _, value_format in self.returned_data_channel_fields
        ]
        lines = [f"_returned_data = {return_line[7:]}"]
        lines.extend([
            "if not isinstance(_returned_data, list):",
            "    raise ValueError('Returned data must be a list.')",
            f"if len(_returned_data) != {len(formats)}:",
            "    raise ValueError('Returned data length does not match its data type channels.')",
            f"_returned_formats = {formats!r}",
            "for _returned_value, _returned_format in zip(_returned_data, _returned_formats):",
            "    if _returned_format == 'integer' and (not isinstance(_returned_value, int) or isinstance(_returned_value, bool)):",
            "        raise ValueError('Returned channel value must be an integer.')",
            "    if _returned_format == 'float' and not isinstance(_returned_value, (int, float)):",
            "        raise ValueError('Returned channel value must be numeric.')",
            "    if _returned_format == 'text' and not isinstance(_returned_value, str):",
            "        raise ValueError('Returned channel value must be text.')",
            "    if _returned_format == 'boolean' and not isinstance(_returned_value, bool):",
            "        raise ValueError('Returned channel value must be boolean.')",
            "return _returned_data",
        ])
        return lines

    def _show_invalid_command(self, message):
        self.testResponse.setText(message)
        QMessageBox.warning(self, "Invalid command", message)

    def _validate_generated_method(self, method_file_text):
        """Reject generated methods with syntax or obvious local-name errors."""
        try:
            module = ast.parse(method_file_text)
        except SyntaxError as error:
            raise ValueError(
                f"Generated command has invalid Python syntax: {error.msg} "
                f"(line {error.lineno})."
            ) from error

        run_method = next(
            (
                node for node in module.body
                if isinstance(node, ast.FunctionDef) and node.name == "run"
            ),
            None,
        )
        if run_method is None:
            raise ValueError("Generated command does not define run(self).")

        known_names = {argument.arg for argument in run_method.args.args}
        known_names.update(dir(builtins))

        def loaded_names(node):
            return {
                child.id for child in ast.walk(node)
                if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load)
            }

        def target_names(node):
            if isinstance(node, ast.Name):
                return {node.id}
            if isinstance(node, (ast.Tuple, ast.List)):
                return set().union(*(target_names(item) for item in node.elts))
            return set()

        def validate_block(statements, known):
            for statement in statements:
                if isinstance(statement, ast.Assign):
                    missing = loaded_names(statement.value) - known
                    if missing:
                        raise ValueError(
                            "Generated command uses an undefined variable: "
                            + ", ".join(sorted(missing))
                        )
                    for target in statement.targets:
                        known.update(target_names(target))
                elif isinstance(statement, ast.AugAssign):
                    missing = loaded_names(statement.value) | loaded_names(statement.target)
                    missing -= known
                    if missing:
                        raise ValueError(
                            "Generated command uses an undefined variable: "
                            + ", ".join(sorted(missing))
                        )
                    known.update(target_names(statement.target))
                elif isinstance(statement, ast.Return):
                    missing = loaded_names(statement.value) - known
                    if missing:
                        raise ValueError(
                            "Generated command returns an undefined variable: "
                            + ", ".join(sorted(missing))
                        )
                elif isinstance(statement, ast.If):
                    missing = loaded_names(statement.test) - known
                    if missing:
                        raise ValueError(
                            "Generated command uses an undefined variable: "
                            + ", ".join(sorted(missing))
                        )
                    validate_block(statement.body, known.copy())
                    validate_block(statement.orelse, known.copy())
                elif isinstance(statement, ast.For):
                    missing = loaded_names(statement.iter) - known
                    if missing:
                        raise ValueError(
                            "Generated command uses an undefined variable: "
                            + ", ".join(sorted(missing))
                        )
                    loop_known = known | target_names(statement.target)
                    validate_block(statement.body, loop_known)
                elif isinstance(statement, ast.Try):
                    validate_block(statement.body, known)

        validate_block(run_method.body, known_names)
        
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
        command_name = self.nameLineEdit.text().strip()

        if not command_name.isidentifier():
            self.nameLineEdit.setText("Invalid Python name")
            return

        method_path = self.methods_folder / f"{command_name}.py"

        if method_path.exists():
            self.nameLineEdit.setText("This name already exists.")
            return

        self.command_name = command_name
        self.method_path = method_path
        
        # new_method_path = pathlib.Path(f"{SAVED_INSTRUMENTS_DIR}/Members/{self.instrument.model}/{self.nameLineEdit.text()}.py")
        # try:
        #     self.method_path.rename(new_method_path)
            
        #     with open(new_method_path, "r") as f:
        #         current_content = f.read()
        #         print(current_content)
        #         old_string = f'command_name = "{self.command_name}"'
        #         new_string = f'command_name = "{self.nameLineEdit.text()}"'
                
        #         if old_string not in current_content:
        #             print(f'"{old_string}" not found. No changes made.')
        #             return
                
        #         new_content = current_content.replace(old_string, new_string)
        #         print(f'Successfully changed "{old_string}" to "{new_string}".')
                
        #     with open(new_method_path, "w") as f:    
        #         f.write(new_content)
            
        #     self.command_name = self.nameLineEdit.text()
        #     self.method_path = new_method_path
                
        # except FileNotFoundError:
        #     print(f"Error: The file '{self.method_path}' was not found.")
        # except FileExistsError:
        #     self.nameLineEdit.setText(f"This name already exists.")
        #     print(f"Error: The file '{self.command_name}' already exists.")
        
        
    def commandTextSaveButton_method(self):
        self.command_text = self.commandText.text()
        # try:
        #     with open(self.method_path, "r") as f:
        #         current_content = f.read()
        #         print(current_content)
        #         old_string = f'command_text = "{self.command_text}"'
        #         new_string = f'command_text = "{self.commandText.text()}"'
                
        #         if old_string not in current_content:
        #                 print(f'"{old_string}" not found. No changes made.')
        #                 return

        #         new_content = current_content.replace(old_string, new_string)
        #         print(f'Successfully changed "{old_string}" to "{new_string}".')
            
        #     with open(self.method_path, "w") as f:    
        #             f.write(new_content)
            
        #     self.command_text = self.commandText.text()
        
        # except FileNotFoundError:
        #     print(f"Error: The file '{self.method_path}' was not found.")
        
    # -------------------------------
    # Data type buttons
    # -------------------------------
    def parameterAddButton_method(self):
        data_name = "Data" + str(self.parameterComboBox.count())
        self.parameterComboBox.addItem(data_name)
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

    def parameterSaveButton_method(self):
        data_name = self.parameterComboBox.currentText()
        self.new_data_list[data_name] = self.parameterDefaultValue.text()
        self.new_test_data_list[data_name] = self.parameterDefaultValue.text()
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
        try:
            self.parameterDefaultValue.setText(self.old_data_list[self.parameterComboBox.currentText()])
        except KeyError:
            pass

    def parameterRemoveButton_method(self):
        data_name = self.parameterComboBox.currentText()
        self.parameterComboBox.removeItem(self.parameterComboBox.currentIndex())
        index = self.testComboBox.findText(data_name)
        self.testComboBox.removeItem(index)
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
        self.communication_syntax = self.comSystemComboBox.currentText()
        # try:
        #     with open(self.method_path, "r") as f:
        #         current_content = f.read()
        #         print(current_content)
        #         old_string = f'communication_syntax = "{self.communication_syntax}"'
        #         new_string = f'communication_syntax = "{self.comSystemComboBox.currentText()}"'
                
        #         if old_string not in current_content:
        #                 print(f'"{old_string}" not found. No changes made.')
        #                 return

        #         new_content = current_content.replace(old_string, new_string)
        #         print(f'Successfully changed "{old_string}" to "{new_string}".')
            
        #     with open(self.method_path, "w") as f:    
        #             f.write(new_content)
        
        # except FileNotFoundError:
        #     print(f"Error: The file '{self.method_path}' was not found.")
    
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
        try:
            self.testValue.setText(self.new_test_data_list[self.testComboBox.currentText()])
        except KeyError:
            pass

    def testExecute_method(self):
        if self.new_function_code == "":
            self.new_function_code = "return None"

        function_code = "".join(
            f"        {line}\n" for line in self.new_function_code.split("\n")
        )

        for data_name, data_value in self.new_test_data_list.items():
            function_code = function_code.replace(f"{{{data_name}}}", data_value)

# ADD THE DRAFT TEST FUNCTION
        draft_script = (
            "def run(self):\n"
            "    try:\n"
            f"{function_code}"
            "    except Exception as e:\n"
            "        print(\"Something went wrong: \" + str(e))\n"
        )
        module_path = (
            f"Tools.saved_instruments."
            f"{self.instrument.model}."
            f"methods.__draft_test__"
        )
# IMPORT AND RUN THE TEST FUNCTION
        try:
            with open(self.test_method_path, "w", encoding="utf-8") as f:
                f.write(draft_script)

            importlib.invalidate_caches()

            if module_path in sys.modules:
                method_module = importlib.reload(sys.modules[module_path])
            else:
                method_module = importlib.import_module(module_path)

            response = method_module.run(self.instrument)
            self.response = response
            self.testResponse.setText(str(response))

        except (ImportError, AttributeError) as e:
            print(f"Error: {e}")
            self.testResponse.setText(f"The file '{self.method_path}' was not found. Did you save your method name?")
        except (IndentationError, SyntaxError) as error:
            self.testResponse.setText(f"Invalid function code: {error.msg}")
        except Exception as e:
            self.testResponse.setText(str(e))
            print(str(e))
    
            
# REMOVE THE TEST FUNCTION
        finally:
            try:
                self.test_method_path.unlink()
            except FileNotFoundError:
                pass

            sys.modules.pop(module_path, None)
            importlib.invalidate_caches()
            

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
        command_name = self.nameLineEdit.text().strip()

        if not command_name.isidentifier():
            self.nameLineEdit.setText("Invalid Python name")
            return

        method_path = self.methods_folder / f"{command_name}.py"

        if method_path.exists():
            self.nameLineEdit.setText("This command already exists.")
            return

        self.command_name = command_name
        self.method_path = method_path

        self.command_text = self.commandText.text()
        self.command_type = self.commandTypeComboBox.currentText()
        self.communication_syntax = self.comSystemComboBox.currentText()

        try:
            self._validate_returned_data_selection()
        except ValueError as error:
            self.testResponse.setText(str(error))
            return

        saving_function_code = ""

        if self.new_function_code == "":
            self.new_function_code = "return None"

        saving_function_code_list = self.new_function_code.split("\n")
        data_manipulation_code_list = self.new_data_manipulation_code.split("\n")

        last_code_line = saving_function_code_list.pop()
        saving_function_code_list.extend(data_manipulation_code_list)
        try:
            saving_function_code_list.extend(
                self._returned_data_validation_code(last_code_line)
            )
        except ValueError as error:
            self.testResponse.setText(str(error))
            return

        for line in saving_function_code_list:
            saving_function_code += "        " + line + "\n"

        for data_name, data_value in self.new_data_list.items():
            saving_function_code = saving_function_code.replace(f"{{{data_name}}}", data_value)

        method_file_text = self.build_method_file_text(saving_function_code)

        try:
            self._validate_generated_method(method_file_text)
        except ValueError as error:
            self._show_invalid_command(str(error))
            return

        try:
            with open(self.method_path, "w", encoding="utf-8") as f:
                f.write(method_file_text)

            self.update_metadata_for_command()
            importlib.invalidate_caches()
            self.window.hide()

        except Exception as e:
            self.testResponse.setText(str(e))
            print(str(e))
#         saving_function_code = ""
#         if self.new_function_code == "":
#             self.new_function_code = "return None"
#         saving_function_code_list = self.new_function_code.split("\n")
        
#         data_manipulation_code_list = self.new_data_manipulation_code.split("\n")
        
# # PUTTING THE FUNCTION AND DATA MANIPULATION TOGETHER
#         last_code_line = saving_function_code_list.pop()
#         saving_function_code_list.extend(data_manipulation_code_list)
#         saving_function_code_list.append(last_code_line)
#         n = len(saving_function_code_list)
        
#         for i in range(0,n):
#             saving_function_code = saving_function_code + "        " + saving_function_code_list[i] + "\n"
        
#         for data_name, data_value in self.new_data_list.items():
#             saving_function_code = saving_function_code.replace(f"{{{data_name}}}", data_value)

# # ADD THE TEST FUNCTION
#         try:
#             with open(self.method_path, "a") as f:
#                 self.method_script = f"""def run(self):
#     try:
# {saving_function_code}
#     except Exception as e:
#         print("Something went wrong: " + e)
# """
#                 print(self.method_script)
#                 f.write(self.method_script)     
#         except FileNotFoundError:
#             print(f"Error: The file '{self.method_path}' was not found.")
            
# # update the metadata
#         self.command_name = self.nameLineEdit.text()
#         self.command_text = self.command_text
#         self.command_type = self.commandTypeComboBox.currentText()
#         self.communication_syntax = self.comSystemComboBox.currentText()

#         self.update_metadata_for_command()

#         importlib.invalidate_caches()
        
            
#         self.window.hide()
    
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
    
    def build_method_file_text(self, saving_function_code):
        return f'''command_name = {self.command_name!r}
command_text = {self.command_text!r}
data_list = {self.new_data_list}
command_type = {self.command_type!r}
communication_syntax = {self.communication_syntax!r}
desired_data_type = {self.desiredDataComboBox.currentText()!r}

function_code = {self.new_function_code!r}
data_manipulation_code = {self.new_data_manipulation_code!r}

def run(self):
    try:
{saving_function_code}
    except Exception as e:
        print("Something went wrong: " + str(e))
'''





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
        self.original_method_file = f"{SAVED_INSTRUMENTS_DIR}/Members/{self.instrument.model}/{self.command_name}_method.py"
        self.copy_method_file = f"{SAVED_INSTRUMENTS_DIR}/Members/{self.instrument.model}/{self.command_name}_method_copy.py"

        try:
            # Use shutil.copy2 to copy the file content and metadata (permissions, timestamps)
            shutil.copy2(self.original_method_file, self.copy_method_file)
            print(f"File copied.")
        except IOError as e:
            print(f"Error copying file: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        
        self.original_method_path = pathlib.Path(f"{SAVED_INSTRUMENTS_DIR}/Members/{self.instrument.model}/{self.command_name}_method_copy.py")
        self.method_path = pathlib.Path(f"{SAVED_INSTRUMENTS_DIR}/Members/{self.instrument.model}/{self.command_name}_method.py")

# CREATE A COPY FILE OF ATTRIBUTES
        self.original_attribute_file = f"{SAVED_INSTRUMENTS_DIR}/Members/{self.instrument.model}/attributes.py"
        self.copy_attribute_file = f"{SAVED_INSTRUMENTS_DIR}/Members/{self.instrument.model}/attributes_copy.py"

        try:
            # Use shutil.copy2 to copy the file content and metadata (permissions, timestamps)
            shutil.copy2(self.original_attribute_file, self.copy_attribute_file)
            print(f"File copied.")
        except IOError as e:
            print(f"Error copying file: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        
        self.original_attribute_path = pathlib.Path(f"{SAVED_INSTRUMENTS_DIR}/Members/{self.instrument.model}/attributes_copy.py")
        self.attribute_path = pathlib.Path(f"{SAVED_INSTRUMENTS_DIR}/Members/{self.instrument.model}/attributes.py")

# GET RID OF THIS FUNCTION IN THE NEW ATTRIBUTE FILE
        attribute_module = importlib.import_module(f"Tools.saved_instruments.Members.{self.instrument.model}.attributes")
        
        functions_dict = getattr(attribute_module, "functions")
        try:
            del functions_dict[self.original_command_name]
        except KeyError:
            pass
        functions_dict = "functions = " + str(functions_dict) + "\n"
        
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
                self.parameterComboBox.addItem(data_name)
                self.testComboBox.addItem(data_name)
            if self.old_data_list:
                self.parameterDefaultValue.setText(self.old_data_list[self.parameterComboBox.currentText()])
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
            self.parameterComboBox.currentIndexChanged.connect(self.change_data_default)
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
        
        new_method_path = pathlib.Path(f"{SAVED_INSTRUMENTS_DIR}/Members/{self.instrument.model}/{self.nameLineEdit.text()}_method.py")
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
    def parameterAddButton_method(self):
        data_name = "Data" + str(self.parameterComboBox.count())
        self.parameterComboBox.addItem(data_name)
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

    def parameterSaveButton_method(self):
        data_name = self.parameterComboBox.currentText()
        self.new_data_list[data_name] = self.parameterDefaultValue.text()
        self.new_test_data_list[data_name] = self.parameterDefaultValue.text()
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
        try:
            self.parameterDefaultValue.setText(self.old_data_list[self.parameterComboBox.currentText()])
        except KeyError:
            pass

    def parameterRemoveButton_method(self):
        data_name = self.parameterComboBox.currentText()
        self.parameterComboBox.removeItem(self.parameterComboBox.currentIndex())
        index = self.testComboBox.findText(data_name)
        self.testComboBox.removeItem(index)
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
        self.command_type = self.commandTypeComboBox.currentText()
        # try:
        #     with open(self.method_path, "r") as f:
        #         current_content = f.read()
        #         print(current_content)
        #         old_string = f'command_type = "{self.command_type}"'
        #         new_string = f'command_type = "{self.commandTypeComboBox.currentText()}"'
                
        #         if old_string not in current_content:
        #                 print(f'"{old_string}" not found. No changes made.')
        #                 return

        #         new_content = current_content.replace(old_string, new_string)
        #         print(f'Successfully changed "{old_string}" to "{new_string}".')
            
        #     with open(self.method_path, "w") as f:    
        #             f.write(new_content)
            
        #     self.command_type = self.commandTypeComboBox.currentText()
        
        # except FileNotFoundError:
        #     print(f"Error: The file '{self.method_path}' was not found.")

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
        self.old_function_code = self.new_function_code
        # try:
        #     with open(self.method_path, "r") as f:
        #         current_content = f.read()
        #         print(current_content)
        #         old_string = f'function_code = \"\"\"{self.old_function_code}\"\"\"'
        #         new_string = f'function_code = \"\"\"{self.new_function_code}\"\"\"'
                
        #         if old_string not in current_content:
        #                 print(f'"{old_string}" not found. No changes made.')
        #                 return

        #         new_content = current_content.replace(old_string, new_string)
        #         print(f'Successfully changed.')
            
        #     with open(self.method_path, "w") as f:    
        #             f.write(new_content)
            
        #     self.old_function_code = self.new_function_code
        
        # except FileNotFoundError:
        #     print(f"Error: The file '{self.method_path}' was not found.")

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
        try:
            self.testValue.setText(self.new_test_data_list[self.testComboBox.currentText()])
        except KeyError:
            pass

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
def run(self):
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
            module_path = f"Tools.saved_instruments.Members.{self.instrument.model}.{self.command_name}"
            if module_path in sys.modules:
                method_module = importlib.reload(sys.modules[module_path])
            else:
                method_module = importlib.import_module(module_path)
            # 2. Get the specific function/attribute from the module using getattr
            method_function = getattr(method_module, f"run")
            
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
        self.old_data_manipulation_code = self.new_data_manipulation_code
        # try:
        #     with open(self.method_path, "r") as f:
        #         current_content = f.read()
        #         print(current_content)
        #         old_string = f'data_manipulation_code = \"\"\"{self.old_data_manipulation_code}\"\"\"'
        #         new_string = f'data_manipulation_code = \"\"\"{self.new_data_manipulation_code}\"\"\"'
                
        #         if old_string not in current_content:
        #                 print(f'"{old_string}" not found. No changes made.')
        #                 return

        #         new_content = current_content.replace(old_string, new_string)
        #         print(f'Successfully changed.')
            
        #     with open(self.method_path, "w") as f:    
        #             f.write(new_content)
            
        #     self.old_data_manipulation_code = self.new_data_manipulation_code
        
        # except FileNotFoundError:
        #     print(f"Error: The file '{self.method_path}' was not found.")

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
                self.method_script = f"""def {self.command_name}(self):
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
                new_string = old_string.replace(f", {self.original_command_name}_method", importing_line)
                
                if old_string not in current_content:
                        print(f'"{old_string}" not found. No changes made.')
                        return

                new_content = current_content.replace(old_string, new_string)
                
                print(f'Successfully changed.')
            
            with open(self.attribute_path, "w") as f:    
                    f.write(new_content)
        
        except FileNotFoundError:
            print(f"Error: The file '{self.attribute_path}' was not found.")
            
        # Modify functions list
        ### GET RID OF THE ORIGINAL FUNCTIONS AND REPLACE FUNCTION LIST
        attribute_module = importlib.import_module(f"Tools.saved_instruments.Members.{self.instrument.model}.attributes")
        
        functions_dict = getattr(attribute_module, "functions")
        
        functions_dict[self.command_name] = f"{self.command_name}_method.{self.command_name}"
        functions_dict = "functions = " + str(functions_dict) + "\n"
        functions_dict = functions_dict.replace(f"'{self.command_name}_method.{self.command_name}'", f"{self.command_name}_method.{self.command_name}")
        
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
            new_method_path = pathlib.Path(f"{SAVED_INSTRUMENTS_DIR}/Members/{self.instrument.model}/{self.original_command_name}_method.py")
            new_attribute_path = pathlib.Path(f"{SAVED_INSTRUMENTS_DIR}/Members/{self.instrument.model}/attributes.py")
            try:
                self.original_method_path.rename(new_method_path)
                self.original_attribute_path.rename(new_attribute_path)
            except FileNotFoundError:
                print(f"Error: The file '{self.attribute_path}' was not found.")  
        except:
            pass
        self.window.close()

        
