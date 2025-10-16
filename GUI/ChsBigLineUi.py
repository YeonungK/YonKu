from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget
from PyQt5.QtGui import QCloseEvent
from PyQt5 import uic
import sys

sys.path.append('C:/Users/szkop/Desktop/YonKu')


class chABigLineUi(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.widget = QWidget()
        uic.loadUi("GUI/ui_files/ch_A_big_line.ui", self.widget)
        
        self.setCentralWidget(self.widget)
        self.setWindowTitle("chA measurement")
        self.resize(100,100)
        
        
    def closeEvent(self, event:QCloseEvent):
        pass

class chBBigLineUi(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.widget = QWidget()
        uic.loadUi("GUI/ui_files/ch_B_big_line.ui", self.widget)
        
        self.setCentralWidget(self.widget)
        self.setWindowTitle("chB measurement")
        self.resize(100,100)
        
        
    def closeEvent(self, event:QCloseEvent):
        pass
    
class chCBigLineUi(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.widget = QWidget()
        uic.loadUi("GUI/ui_files/ch_C_big_line.ui", self.widget)
        
        self.setCentralWidget(self.widget)
        self.setWindowTitle("chC measurement")
        self.resize(100,100)
        
        
    def closeEvent(self, event:QCloseEvent):
        pass
    
class chDBigLineUi(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.widget = QWidget()
        uic.loadUi("GUI/ui_files/ch_D_big_line.ui", self.widget)
        
        self.setCentralWidget(self.widget)
        self.setWindowTitle("chD measurement")
        self.resize(100,100)
        
        
    def closeEvent(self, event:QCloseEvent):
        pass