from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget
from PyQt5.QtGui import QCloseEvent
from PyQt5 import uic
import sys
import sys
import re
import types
import pathlib
import importlib


from project_paths import GUI_DIR

class manual_edit_ui(QWidget):
    def __init__(self, current_function_code):
        super().__init__()
        
        uic.loadUi(f"{GUI_DIR}/ui_files/manual_edit_ui.ui", self)
        
        self.code = current_function_code
        self.manualEditDisplay.setPlainText(self.code)

    
        self.manualEditSave.clicked.connect(self.manualEditSave_method)
    
    def manualEditSave_method(self):
        self.code = self.manualEditDisplay.toPlainText()
        
    