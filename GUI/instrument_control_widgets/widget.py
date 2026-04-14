import sys

sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')


from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox, QLineEdit
from PyQt5.QtCore import QTimer, Qt
from PyQt5 import uic
from functools import partial
import os
import json
import importlib

class widget(QWidget):
    def __init__(self, instrument, ui_path):
        super().__init__()
        
        self.instrument = instrument
        self.instrument_model = self.instrument.model
        self.instrument_name = self.instrument.name
        self.ui_path = ui_path
        uic.loadUi(ui_path, self)
        
        self.bind_dynamic_signals()
        
    def sanitize_name(self, name: str) -> str:
        clean = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in str(name))
        if not clean:
            clean = "unnamed"
        if clean[0].isdigit():
            clean = "_" + clean
        return clean

    def bind_dynamic_signals(self):
        
        json_path = f"GUI/ui_files/instrument_control_uis/{self.instrument_model}_ui.json"
        
        if not os.path.exists(json_path):
            print(f"[ERROR] UI definition file not found: {json_path}")
            return
        
        # Load JSON
        try:
           with open(json_path, "r", encoding="utf-8") as f:
            ui_definition = json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load UI definition: {e}")
            return
        
            # Bind signals
        for category_name, components in ui_definition.items():
            safe_category = self.sanitize_name(category_name)

            for component in components:
                component_name = component.get("name", "component")
                safe_component = self.sanitize_name(component_name)

                base = f"{safe_category}_{safe_component}"

                # READ BUTTON
                if component.get("read", False):
                    read_btn = self.findChild(QPushButton, f"{base}_readButton")

                    if read_btn:
                        read_btn.clicked.connect(
                            partial(self.handle_read, category_name, component)
                        )
                    else:
                        print(f"[WARN] Read button not found: {base}_readButton")

                # WRITE BUTTON
                if component.get("write", False):
                    write_btn = self.findChild(QPushButton, f"{base}_writeButton")

                    if write_btn:
                        write_btn.clicked.connect(
                            partial(self.handle_write, category_name, component)
                        )
                    else:
                        print(f"[WARN] Write button not found: {base}_writeButton")
        
    def get_component_widget(self, category_name: str, component: dict):
        """
        Find the main input widget for a component.
        Returns either QLineEdit, QComboBox, or None.
        """
        safe_category = self.sanitize_name(category_name)
        safe_component = self.sanitize_name(component.get("name", "component"))
        base = f"{safe_category}_{safe_component}"

        comp_type = component.get("type", 1)

        if comp_type == 1:
            return self.findChild(QLineEdit, f"{base}_lineEdit")
        if comp_type == 2:
            return self.findChild(QComboBox, f"{base}_comboBox")

        return self.findChild(QLineEdit, f"{base}_lineEdit")

    def handle_read(self, category_name: str, component: dict):
        """
        Called when a Read button is pressed.
        Reads from the instrument and updates the UI widget.
        """
        widget = self.get_component_widget(category_name, component)
        command_name = component.get("read_command", "")

        if widget is None:
            print(f"Read failed: widget not found for {category_name} / {component.get('name')}")
            return

        try:
            # IMPORT AND RUN THE TEST FUNCTION
            module_path = f"Tools.saved_instruments.Members.{self.instrument.model}.attributes"
            if module_path in sys.modules:
                method_module = importlib.reload(sys.modules[module_path])
            else:
                method_module = importlib.import_module(module_path)
            # 2. Get the specific function/attribute from the module using getattr
            method_function = method_module.read_functions[command_name]
            value = method_function(self.instrument)
            print(f"This is the respone: {value}")
            
            # print it on component widget
            if isinstance(widget, QLineEdit):
                widget.setText(str(value))

            elif isinstance(widget, QComboBox):
                text_value = str(value)
                index = widget.findText(text_value)
                if index >= 0:
                    widget.setCurrentIndex(index)
                else:
                    widget.addItem(text_value)
                    widget.setCurrentIndex(widget.count() - 1)

        except (ImportError, AttributeError) as e:
            print(f"Error: {e}")
            # self.testResponse.setText(f"The file '{self.method_path}' was not found. Did you save your method name?")
        except IndentationError:
            print("IndentationError: Please check the indentation of your method code.")
            # self.testResponse.setText("The function code is empty.")
        except Exception as e:
            print(e)

    def handle_write(self, category_name: str, component: dict):
        """
        Called when a Write button is pressed.
        Gets the current UI value and sends it to the instrument.
        """
        widget = self.get_component_widget(category_name, component)
        command_name = component.get("write_command", "")

        if widget is None:
            print(f"Write failed: widget not found for {category_name} / {component.get('name')}")
            return

        try:
            if isinstance(widget, QLineEdit):
                value = widget.text()

            elif isinstance(widget, QComboBox):
                value = widget.currentText()

            else:
                print(f"Write failed: unsupported widget for {category_name} / {component.get('name')}")
                return

             # IMPORT AND RUN THE TEST FUNCTION
            module_path = f"Tools.saved_instruments.Members.{self.instrument.model}.attributes"
            if module_path in sys.modules:
                method_module = importlib.reload(sys.modules[module_path])
            else:
                method_module = importlib.import_module(module_path)
            # 2. Get the specific function/attribute from the module using getattr
            method_function = method_module.write_functions[command_name]
            method_function(self.instrument)
            
        except (ImportError, AttributeError) as e:
            print(f"Error: {e}")
            # self.testResponse.setText(f"The file '{self.method_path}' was not found. Did you save your method name?")
        except IndentationError:
            print("IndentationError: Please check the indentation of your method code.")
            # self.testResponse.setText("The function code is empty.")
        except Exception as e:
            print(f"Write failed for {category_name} / {component.get('name')}: {e}")