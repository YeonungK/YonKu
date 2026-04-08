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
import json
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from GUI import ManualEditUi as meu


from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget, QMessageBox, QAction

sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')


class ui_edit_setting_ui(QWidget):
    _GENERIC_NAME_RE = re.compile(r".*_\d+$")
    
    def __init__(self, instrument, data_list, interface, window):
        super().__init__()
        print("loadUi")
        uic.loadUi("GUI/ui_files/ui_edit.ui", self)
        
        self.instrument = instrument
        self.data_list = data_list
        self.save_file = False
        self.interface = str(interface)
        self.window = window
        self.instrument_name_label.setText(self.data_list['model'])
        
        # empty ui config
        self.ui_definition = {}

        # signals connect
        self.show_current_ui_pushButton.clicked.connect(self.load_current_ui)
        self.category_remove_pushButton.clicked.connect(lambda: self.remove_category(self.choose_category_comboBox.currentText())) # not complete
        self.category_add_pushButton.clicked.connect(lambda: self.add_category(self.add_category_lineEdit.text()))
        self.component_remove_pushButton.clicked.connect(lambda: self.remove_component(self.choose_category_comboBox.currentText(), self.choose_component_comboBox.currentText())) # not complete
        self.command_list_pushButton.clicked.connect(self.open_command_list_window)
        self.add_component_pushButton.clicked.connect(self.add_component)
        self.save_pushButton.clicked.connect(self.translate_instrument_definition_to_ui)
        
        
    def load_current_ui(self):
        self.mdiWindow = QMdiSubWindow()
        self.mdiWidget = QWidget()
        
        json_file_path = f"GUI/ui_files/instrument_control_uis/{self.data_list['model']}_ui.json"
        if not os.path.exists(json_file_path):
            print("You can't edit this UI")
        else:
            with open(json_file_path, "r") as f:
                self.ui_definition = json.load(f)
            uic.loadUi(f"GUI/ui_files/instrument_control_uis/{self.data_list['model']}_ui.ui", self.mdiWidget)
            self.mdiWindow.setWidget(self.mdiWidget)
            self.mdiWindow.setWindowTitle("Current Ui")
            self.current_ui_mdiArea.addSubWindow(self.mdiWindow)
            area_size = self.current_ui_mdiArea.size()
            print(area_size)
            self.mdiWindow.resize(area_size)
            self.mdiWindow.show()
            self.mdiWindow.move(0,0)
    
    

    def remove_category(self):
        if self.choose_category_comboBox.count() == 0:
            self.add_category_lineEdit.setText("No category to remove")
            return
        category_name = self.choose_category_comboBox.currentText()
        del self.ui_definition[category_name]
    
    def add_category(self, category_name):
        if category_name in self.ui_definition:
            self.add_category_lineEdit.setText("The category name already exists.")
            return
        
        self.ui_definition[category_name] = []

    def remove_component(self):
        if self.choose_category_comboBox.count() == 0:
            self.add_category_lineEdit.setText("No category to remove")
            return
        if self.choose_component_comboBox.count() == 0:
            self.add_category_lineEdit.setText("No component to remove")
            return
        category_name = self.choose_category_comboBox.currentText()
        component_name = self.choose_component_comboBox.currentText()
        components = self.ui_definition[category_name]
        for i, component in enumerate(components):
            if component["name"] == component_name:
                del components[i]
                return
    
    def open_command_list_window(self):
        pass

    def add_write_button(self):
        pass

    def add_read_button(self):
        pass

    def add_component(self, category_name, component_name, component_type, command_name, read=True, write=True, exp_readonly=False):
        if category_name not in self.ui_definition:
            QMessageBox.warning(self, "Warning", f"Category '{category_name}' does not exist.")
            return
        
        components = self.ui_definition[category_name]
        for i, component in enumerate(components):
            if component["name"] == component_name:
                QMessageBox.warning(self, "Warning", f"Component '{component_name}' already exists in category '{category_name}'.")
                return
            
        component_info = {
            "name": component_name,
            "type": component_type,
            "command": command_name,
            "read": read,
            "write": write,
            "exp_readonly": exp_readonly
        }
        self.ui_definition[category_name].append(component_info)


    
    
    
    
    
    
    def remove_component(self, category_name, component_name):
        if category_name not in self.ui_definition:
            QMessageBox.warning(self, "Warning", f"Category '{category_name}' does not exist.")
            return
        
        components = self.ui_definition[category_name]
        for i, component in enumerate(components):
            if component["name"] == component_name:
                del components[i]
                return
        
        QMessageBox.warning(self, "Warning", f"Component '{component_name}' not found in category '{category_name}'.")

    def save_instrument_definition(path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    
    def translate_instrument_definition_to_ui(instrument_definition):
        """
        Convert an instrument_definition dictionary into a Qt .ui XML string.

        Expected input structure:
        {
            "window_title": str,
            "instrument_name": str,
            "rows": [
                {
                    "label": str,
                    "line_edit_name": str,
                    "button1_text": str,
                    "button2_text": str
                },
                ...
            ]
        }
        """

        def add_string_property(parent, name, value):
            prop = SubElement(parent, "property", {"name": name})
            string_elem = SubElement(prop, "string")
            string_elem.text = value
            return prop

        def add_geometry_property(parent, x, y, width, height):
            prop = SubElement(parent, "property", {"name": "geometry"})
            rect = SubElement(prop, "rect")

            x_elem = SubElement(rect, "x")
            x_elem.text = str(x)

            y_elem = SubElement(rect, "y")
            y_elem.text = str(y)

            w_elem = SubElement(rect, "width")
            w_elem.text = str(width)

            h_elem = SubElement(rect, "height")
            h_elem.text = str(height)

            return prop
    
        # Root <ui>
        ui = Element("ui", {"version": "4.0"})

        # <class>Form</class>
        class_elem = SubElement(ui, "class")
        class_elem.text = "Form"

        # Main widget
        form = SubElement(ui, "widget", {"class": "QWidget", "name": "Form"})
        add_geometry_property(form, 0, 0, 600, 400)
        add_string_property(form, "windowTitle", instrument_definition.get("window_title", "Form"))

        # Main vertical layout
        main_layout = SubElement(form, "layout", {"class": "QVBoxLayout", "name": "verticalLayout"})

        # Instrument container item
        container_item = SubElement(main_layout, "item")
        container = SubElement(container_item, "widget", {"class": "QWidget", "name": "instrumentContainer"})
        container_layout = SubElement(container, "layout", {"class": "QVBoxLayout", "name": "instrumentContainerLayout"})

        # Instrument name label
        title_item = SubElement(container_layout, "item")
        title_label = SubElement(title_item, "widget", {"class": "QLabel", "name": "instrumentTitleLabel"})
        add_string_property(title_label, "text", instrument_definition.get("instrument_name", "Instrument"))

        # Content widget
        content_item = SubElement(container_layout, "item")
        content_widget = SubElement(content_item, "widget", {"class": "QWidget", "name": "instrumentContent"})
        content_layout = SubElement(content_widget, "layout", {"class": "QVBoxLayout", "name": "instrumentContentLayout"})

        # Add rows
        rows = instrument_definition.get("rows", [])
        for index, row in enumerate(rows, start=1):
            row_item = SubElement(content_layout, "item")

            row_widget = SubElement(
                row_item,
                "widget",
                {"class": "QWidget", "name": f"parameterRowWidget{index}"}
            )

            row_layout = SubElement(
                row_widget,
                "layout",
                {"class": "QHBoxLayout", "name": f"parameterRowLayout{index}"}
            )

            # Label
            label_item = SubElement(row_layout, "item")
            label_widget = SubElement(
                label_item,
                "widget",
                {"class": "QLabel", "name": f"parameterLabel{index}"}
            )
            add_string_property(label_widget, "text", row.get("label", f"Parameter {index}"))

            # Line edit
            line_item = SubElement(row_layout, "item")
            SubElement(
                line_item,
                "widget",
                {
                    "class": "QLineEdit",
                    "name": row.get("line_edit_name", f"parameterLineEdit{index}")
                }
            )

            # Button 1
            button1_item = SubElement(row_layout, "item")
            button1_widget = SubElement(
                button1_item,
                "widget",
                {"class": "QPushButton", "name": f"button1_{index}"}
            )
            add_string_property(button1_widget, "text", row.get("button1_text", "Apply"))

            # Button 2
            button2_item = SubElement(row_layout, "item")
            button2_widget = SubElement(
                button2_item,
                "widget",
                {"class": "QPushButton", "name": f"button2_{index}"}
            )
            add_string_property(button2_widget, "text", row.get("button2_text", "Reset"))

        # Required empty tags
        SubElement(ui, "resources")
        SubElement(ui, "connections")

        # Pretty-print XML
        rough_xml = tostring(ui, encoding="utf-8")
        pretty_xml = minidom.parseString(rough_xml).toprettyxml(indent=" ")

        return pretty_xml
            
            
            