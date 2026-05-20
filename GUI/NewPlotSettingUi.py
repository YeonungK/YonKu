from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget
from PyQt5 import uic
import sys

from project_paths import GUI_DIR
        


class create_plot_setting_ui(QWidget):
    def __init__(self, available_data_types=None):
        super().__init__()


        uic.loadUi(f"{GUI_DIR}/ui_files/new_plot_setting.ui", self)

        self.available_data_types = available_data_types or ["time"]

        self.xAxisUnitComboBox.clear()
        self.yAxisUnitComboBox.clear()

        self.xAxisUnitComboBox.addItems(self.available_data_types)
        self.yAxisUnitComboBox.addItems(self.available_data_types)

        self.xAxisUnit = self.available_data_types[0]
        self.yAxisUnit = self.available_data_types[0]

        self.xAxisUnit = "temperature"
        self.yAxisUnit = "temperature"

        
        self.xAxisHiLim = "auto"
        self.xAxisLoLim = "auto"
        self.yAxisHiLim = "auto"
        self.yAxisLoLim = "auto"
        
        self.tickVal = "auto"
        self.gridLine = False
   
    def update_values(self):
        
        self.xAxisUnit = self.xAxisUnitComboBox.currentText()
        self.yAxisUnit = self.yAxisUnitComboBox.currentText()

        self.xAxisHiLim = self.xAxisHiLimLineEdit.text()
        self.xAxisLoLim = self.xAxisLoLimLineEdit.text()
        self.yAxisHiLim = self.yAxisHiLimLineEdit.text()
        self.yAxisLoLim = self.yAxisLoLimLineEdit.text()

        self.tickVal = self.TicValLineEdit.text()
        self.gridLine = self.gridLineCheckBox.isChecked()
        self.symbol = self.symbolComboBox.currentText()
                
        