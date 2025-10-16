import sys

sys.path.append('C:/Users/szkop/Desktop/YonKu')

import numpy as np
import h5py
import time
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox
from PyQt5.QtCore import QTimer, Qt


class ShowHidePlotUi(QWidget):
    def __init__(self):
        super().__init__()
        
        

