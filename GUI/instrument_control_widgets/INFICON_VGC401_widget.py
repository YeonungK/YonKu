import sys

sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')


from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5 import uic

class pressureGauge_widget(QWidget):
    def __init__(self):
        super().__init__()
        
        uic.loadUi('GUI/ui_files/instrument_control_uis/INFICON_VGC401_ui.ui', self)
        
        self.startButton.clicked.connect(self.change_state)
        
    def change_state(self):
        
        if self.startButton.isChecked():
            self.startButton.setText("Stop Measurement")

        else:
            self.startButton.setText("Start Measurement")
        
        