import sys
import importlib

sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')


from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5 import uic

class disconnected_devices_widget(QWidget):
    def __init__(self, disconnected_dict):
        super().__init__()
        
        uic.loadUi('GUI/ui_files/disconnected_instruments.ui', self)
        
        self.dict = disconnected_dict
    
        for device_model, instrument in self.dict.items():
            self.disconnected_inst_comboBox.addItem(device_model)
        
        self.display_data_type()
        
        self.disconnected_inst_comboBox.currentIndexChanged.connect(self.display_data_type)
        
    
    def display_data_type(self):
        self.sup_data_type_comboBox.clear()
        
        model_name = self.disconnected_inst_comboBox.currentText()
        instrument = self.dict[model_name]
        
        for data_type, data_ch in instrument.data_type.items():
            text = f"{data_type} "
        for data_type, unit in instrument.data_unit.items():
            text = text + f"({unit})"
        
        self.sup_data_type_comboBox.addItem(text)
        
        