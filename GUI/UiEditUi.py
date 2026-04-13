from cProfile import label

from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget, QMessageBox, QAction
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
from GUI import ManualEditUi as meu, CommandListUi as clu


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
        self.mdiWindow = None
        self.instrument_name_label.setText(self.data_list['model'])
        
        # empty ui config
        self.ui_definition = {}

        # load ui config if exists
        self.json_file_path = f"GUI/ui_files/instrument_control_uis/{self.data_list['model']}_ui.json"
        if os.path.exists(self.json_file_path):
            with open(self.json_file_path, "r") as f:
                self.ui_definition = json.load(f)
        else:
            print(self.json_file_path)
            print("You can't edit this UI")
            self.save_pushButton.setEnabled(False)

        # fill the category and component comboBoxes
        self.update_category_combobox()
        self.update_component_combobox()
        
        # disable the command lists
        self.read_command_frame.setEnabled(False)
        self.write_command_frame.setEnabled(False)

        # signals connect
        self.show_current_ui_pushButton.clicked.connect(self.load_current_ui)
        self.category_remove_pushButton.clicked.connect(self.remove_category) # not complete
        self.category_add_pushButton.clicked.connect(lambda: self.add_category(self.add_category_lineEdit.text()))
        self.component_remove_pushButton.clicked.connect(self.remove_component) # not complete
        self.add_read_checkBox.stateChanged.connect(self.enable_read_command)
        self.read_command_list_pushButton.clicked.connect(lambda: self.open_command_list_window(self.read_command_name_label))
        self.add_write_checkBox.stateChanged.connect(self.enable_write_command)
        self.write_command_list_pushButton.clicked.connect(lambda: self.open_command_list_window(self.write_command_name_label))
        self.add_component_pushButton.clicked.connect(self.add_component)
        self.save_pushButton.clicked.connect(self.save_instrument_definition)
        self.choose_category_comboBox.currentTextChanged.connect(self.update_component_combobox)
        
    def enable_read_command(self):
        if self.add_read_checkBox.isChecked():
            self.read_command_frame.setEnabled(True)
        else:
            self.read_command_frame.setEnabled(False)
    
    def enable_write_command(self):
        if self.add_write_checkBox.isChecked():
            self.write_command_frame.setEnabled(True)
        else:
            self.write_command_frame.setEnabled(False)
        
    def update_category_combobox(self):
        self.choose_category_comboBox.clear()
        for category in self.ui_definition.keys():
            self.choose_category_comboBox.addItem(category)
        
        self.update_component_combobox()

    def update_component_combobox(self):
        self.choose_component_comboBox.clear()
        category_name = self.choose_category_comboBox.currentText()
        if category_name in self.ui_definition:
            components = self.ui_definition[category_name]
            for component in components:
                self.choose_component_comboBox.addItem(component["name"])
    

    def load_current_ui(self):
        if self.mdiWindow != None:
            self.mdiWindow.close()
        
        self.mdiWindow = QMdiSubWindow()
        self.mdiWidget = QWidget()
        
        if not os.path.exists(self.json_file_path):
            print(self.json_file_path)
            print("You can't edit this UI")
        else:
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

        # update comboBoxes
        self.update_category_combobox()
        self.update_component_combobox()
    
    def add_category(self, category_name):
        if category_name in self.ui_definition:
            self.add_category_lineEdit.setText("The category name already exists.")
            return
        
        self.ui_definition[category_name] = []

        # update comboBoxes
        self.update_category_combobox()
        self.update_component_combobox()
    

    def remove_component(self):
        if self.choose_category_comboBox.count() == 0:
            self.component_lineEdit.setText("Choose a category to remove")
            return
        if self.choose_component_comboBox.count() == 0:
            self.component_lineEdit.setText("No component to remove")
            return
        category_name = self.choose_category_comboBox.currentText()
        component_name = self.choose_component_comboBox.currentText()
        components = self.ui_definition[category_name]
        for i, component in enumerate(components):
            if component["name"] == component_name:
                del components[i]
                
        # update component comboBox
        self.update_component_combobox()
    
    def open_command_list_window(self, command_name_label):
        self.CommandListWin = QMainWindow()
        self.CommandListWid = clu.command_list_ui(self.instrument, self.CommandListWin, True, command_name_label)
        self.CommandListWin.setCentralWidget(self.CommandListWid)
        
        self.CommandListWin.setWindowTitle(f"{self.instrument.model} Command List")
        self.CommandListWin.resize(600, 420)
        self.CommandListWin.move(500, 200)
        
        self.CommandListWin.show()
        
    

    def add_component(self):
        if self.choose_category_comboBox.count() == 0:
            self.component_lineEdit.setText("Make a category to add a component to")
            return
        
        category_name = self.choose_category_comboBox.currentText()
        component_name = self.component_lineEdit.text()
        component_type = self.widget_type_comboBox.currentIndex()
        add_read = self.add_read_checkBox.isChecked()
        read_command_name = self.read_command_name_label.text()
        add_write = self.add_write_checkBox.isChecked()
        write_command_name = self.write_command_name_label.text()
        exp_readonly = self.read_only_checkBox.isChecked()
        
        if category_name not in self.ui_definition:
            self.add_category_lineEdit.setText("The category doesn't exist. Something is wrong.")
            return
        
        components = self.ui_definition[category_name]
        for i, component in enumerate(components):
            if component["name"] == component_name:
                self.component_lineEdit.setText("This component name already exists")
                return
            
        component_info = {
            "name": component_name,
            "type": component_type,
            "read": add_read,
            "read_command": read_command_name,
            "write": add_write,
            "write_command": write_command_name,
            "exp_readonly": exp_readonly
        }
        self.ui_definition[category_name].append(component_info)
        print(self.ui_definition)

        # update component comboBox
        self.update_component_combobox()
    

    def save_instrument_definition(self):
        # save the json config file
        json_file_path = f"GUI/ui_files/instrument_control_uis/{self.data_list['model']}_ui.json"   
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(self.ui_definition, f, indent=4)

        # save the .ui file
        ui_xml = self.ui_definition_to_xml(save_path=f"GUI/ui_files/instrument_control_uis/{self.data_list['model']}_ui.ui")

    
    # translates the ui_config json data(python dict data) to xml and saves it

    def ui_definition_to_xml(self, save_path=None):

        def sanitize_name(name):
            clean = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in str(name))
            if not clean:
                clean = "unnamed"
            if clean[0].isdigit():
                clean = "_" + clean
            return clean

        def add_string_property(parent, name, value):
            prop = SubElement(parent, "property", {"name": name})
            string_elem = SubElement(prop, "string")
            string_elem.text = "" if value is None else str(value)

        def add_bool_property(parent, name, value):
            prop = SubElement(parent, "property", {"name": name})
            bool_elem = SubElement(prop, "bool")
            bool_elem.text = "true" if value else "false"

        def add_rect_property(parent, x, y, w, h):
            prop = SubElement(parent, "property", {"name": "geometry"})
            rect = SubElement(prop, "rect")

            for tag, val in zip(["x", "y", "width", "height"], [x, y, w, h]):
                elem = SubElement(rect, tag)
                elem.text = str(val)

        def add_number_property(parent, name, value):
            prop = SubElement(parent, "property", {"name": name})
            number_elem = SubElement(prop, "number")
            number_elem.text = str(value)

        def add_layout_item(parent_layout, row=None, column=None):
            attrs = {}
            if row is not None:
                attrs["row"] = str(row)
            if column is not None:
                attrs["column"] = str(column)
            return SubElement(parent_layout, "item", attrs)

        def create_component_row(parent_layout, category_name, component):
            component_name = component.get("name", "component")
            comp_type = component.get("type", 1)
            allow_write = component.get("write", False)
            allow_read = component.get("read", False)
            exp_readonly = component.get("exp_readonly", False)

            cat = sanitize_name(category_name)
            comp = sanitize_name(component_name)
            base = f"{cat}_{comp}"

            row_item = SubElement(parent_layout, "item")
            row_widget = SubElement(row_item, "widget", {
                "class": "QWidget",
                "name": f"{base}_rowWidget"
            })

            row_layout = SubElement(row_widget, "layout", {
                "class": "QHBoxLayout",
                "name": f"{base}_rowLayout"
            })

            # Component label
            label_item = SubElement(row_layout, "item")
            label = SubElement(label_item, "widget", {
                "class": "QLabel",
                "name": f"{base}_label"
            })
            add_string_property(label, "text", component_name)

            # Component widget
            input_item = SubElement(row_layout, "item")

            if comp_type == 1:
                widget = SubElement(input_item, "widget", {
                    "class": "QLineEdit",
                    "name": f"{base}_lineEdit"
                })
                add_bool_property(widget, "readOnly", exp_readonly)

            elif comp_type == 2:
                widget = SubElement(input_item, "widget", {
                    "class": "QComboBox",
                    "name": f"{base}_comboBox"
                })

            else:
                widget = SubElement(input_item, "widget", {
                    "class": "QLineEdit",
                    "name": f"{base}_lineEdit"
                })
                add_bool_property(widget, "readOnly", exp_readonly)

            # Read button
            if allow_read:
                read_item = SubElement(row_layout, "item")
                read_btn = SubElement(read_item, "widget", {
                    "class": "QPushButton",
                    "name": f"{base}_readButton"
                })
                add_string_property(read_btn, "text", "Read")

            # Write button
            if allow_write:
                write_item = SubElement(row_layout, "item")
                write_btn = SubElement(write_item, "widget", {
                    "class": "QPushButton",
                    "name": f"{base}_writeButton"
                })
                add_string_property(write_btn, "text", "Write")
                
        def add_empty_label(parent_layout, category_name):
            cat = sanitize_name(category_name)

            item = SubElement(parent_layout, "item")

            label = SubElement(item, "widget", {
                "class": "QLabel",
                "name": f"{cat}_emptyLabel"
            })

            add_string_property(label, "text", "No components")

            prop = SubElement(label, "property", {"name": "alignment"})
            align = SubElement(prop, "set")
            align.text = "Qt::AlignCenter"

        # Root UI
        ui = Element("ui", {"version": "4.0"})
        SubElement(ui, "class").text = "Form"

        # Main form
        form = SubElement(ui, "widget", {"class": "QWidget", "name": "Form"})
        add_rect_property(form, 0, 0, 1000, 700)
        add_string_property(form, "windowTitle", "Instrument Control")

        # Main layout of the whole form
        main_layout = SubElement(form, "layout", {
            "class": "QVBoxLayout",
            "name": "verticalLayout"
        })

        # Scroll area
        scroll_item = SubElement(main_layout, "item")
        scroll_area = SubElement(scroll_item, "widget", {
            "class": "QScrollArea",
            "name": "scrollArea"
        })
        add_bool_property(scroll_area, "widgetResizable", True)

        # Scroll content widget
        scroll_content = SubElement(scroll_area, "widget", {
            "class": "QWidget",
            "name": "scrollAreaWidgetContents"
        })
        add_rect_property(scroll_content, 0, 0, 960, 660)

        # Grid layout inside the scroll area
        grid_layout = SubElement(scroll_content, "layout", {
            "class": "QGridLayout",
            "name": "gridLayout"
        })


        # Categories
        for index, (category_name, components) in enumerate(self.ui_definition.items(), start=1):
            cat = sanitize_name(category_name)

            row = (index - 1) // 2
            column = 0 if index % 2 == 1 else 1

            item = add_layout_item(grid_layout, row=row, column=column)

            container = SubElement(item, "widget", {
                "class": "QWidget",
                "name": f"{cat}_container"
            })

            layout = SubElement(container, "layout", {
                "class": "QVBoxLayout",
                "name": f"{cat}_layout"
            })

            # Category label
            title_item = SubElement(layout, "item")
            title = SubElement(title_item, "widget", {
                "class": "QLabel",
                "name": f"{cat}_label"
            })
            add_string_property(title, "text", category_name)

            # Component rows
            
            if not components:
                add_empty_label(layout, category_name)

            else:
                for comp in components:
                    create_component_row(layout, category_name, comp)
            
            

        SubElement(ui, "resources")
        SubElement(ui, "connections")

        xml = minidom.parseString(tostring(ui, encoding="utf-8")).toprettyxml(indent=" ")
        print(xml)

        if save_path:
            print("path received")
            directory = os.path.dirname(save_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(xml)

        return xml
                
            
            