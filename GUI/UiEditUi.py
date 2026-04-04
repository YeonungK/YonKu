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
        self.show_current_ui_pushButton.clicked.connect(self.load_current_ui)
        
        
    def load_current_ui(self):
        self.mdiWindow = QMdiSubWindow()
        self.mdiWidget = QWidget()
        uic.loadUi(f"GUI/ui_files/instrument_control_uis/{self.data_list['model']}_ui.ui", self.mdiWidget)
        self.mdiWindow.setWidget(self.mdiWidget)
        self.mdiWindow.setWindowTitle("Current Ui")
        self.current_ui_mdiArea.addSubWindow(self.mdiWindow)
        area_size = self.current_ui_mdiArea.size()
        print(area_size)
        self.mdiWindow.resize(area_size)
        self.mdiWindow.show()
        self.mdiWindow.move(0,0)
        
        