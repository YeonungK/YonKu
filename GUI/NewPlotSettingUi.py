from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget
from PyQt5 import uic
import sys

from project_paths import GUI_DIR
        


class create_plot_setting_ui(QWidget):
    def __init__(self):
        super().__init__()

        uic.loadUi(f"{GUI_DIR}/ui_files/new_plot_setting.ui", self)

        self.xAxisUnit = "temperature"
        self.yAxisUnit = "temperature"

        
        self.xAxisHiLim = "auto"
        self.xAxisLoLim = "auto"
        self.yAxisHiLim = "auto"
        self.yAxisLoLim = "auto"
        
        self.tickVal = "auto"
        self.gridLine = False
   
    def update_values(self):
        
        match self.xAxisUnitComboBox.currentIndex():
            case 0:
                self.xAxisUnit = "temperature"
                
            case 1:
                self.xAxisUnit = "resistance"
                
            case 2:
                self.xAxisUnit = "lockIn"
                
            case 3:
                self.xAxisUnit = "lockIn2"
                
            case 4:
                self.xAxisUnit = "field"
                
            case 5:
                self.xAxisUnit = "current"
                
            case 6:
                self.xAxisUnit = "time"
                
            case _:
                self.xAxisUnit = 'time'
        
        match self.yAxisUnitComboBox.currentIndex():
            case 0:
                self.yAxisUnit = "temperature"
                
            case 1:
                self.yAxisUnit = "resistance"
            case 2:
                self.yAxisUnit = "lockIn"
            case 3:
                self.yAxisUnit = "lockIn2"
            case 4:
                self.yAxisUnit = "field"
            case 5:
                self.yAxisUnit = "current"
            case 6:
                self.yAxisUnit = "time"
            case _:
                self.yAxisUnit = "temperature"
        
        
        self.xAxisHiLim = self.xAxisHiLimLineEdit.text()
        self.xAxisLoLim = self.xAxisLoLimLineEdit.text()
        self.yAxisHiLim = self.yAxisHiLimLineEdit.text()
        self.yAxisLoLim = self.yAxisLoLimLineEdit.text()
        
        
        self.tickVal = self.TicValLineEdit.text()
        self.gridLine = self.gridLineCheckBox.isChecked()
        self.symbol = self.symbolComboBox.currentText()
                
        