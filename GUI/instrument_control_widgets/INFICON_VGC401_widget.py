import sys

sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')


from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QObject, QThread
from PyQt5 import uic

class pressureGauge_widget(QWidget):
    def __init__(self, instrument):
        super().__init__()
        
        self.instrument = instrument
        uic.loadUi('GUI/ui_files/instrument_control_uis/INFICON_VGC401_ui.ui', self)
        
        
        # [---------pressure gauge ui output signals---------]
        
        self.startDisplay.clicked.connect(self.pressureGauge_thread) # [/]
    
    # [-------functions--------]
      
    
    def pressureGauge_thread(self):
        print("pressure reading start")
        
        self.pressure_worker = pressureGauge_worker(self.instrument, 2000, self.stopDisplay, self.pressureGaugeLineEdit)
        self.pressure_worker_thread = QThread()
        self.pressure_worker.moveToThread(self.pressure_worker_thread)
        
        self.pressure_worker_thread.started.connect(self.pressure_worker.start_reading)
        self.pressure_worker.finished.connect(self.pressure_worker_thread.quit)
        self.pressure_worker_thread.finished.connect(self.pressure_worker.deleteLater)
        self.pressure_worker_thread.finished.connect(self.pressure_worker_thread.deleteLater)
        
        self.pressure_worker_thread.start()
        
            # [/]
        
    
"""worker class for measuring pressureGauge (thread)"""
class pressureGauge_worker(QObject):
    finished = pyqtSignal()
    def __init__(self, instrument, period, stopDisplayButton, pressureLineEdit):
        super().__init__()
        
        self.instrument = instrument
        self.period = period
        self.stopDisplayButton = stopDisplayButton
        self.pressureLineEdit = pressureLineEdit
        
        self.stopDisplayButton.clicked.connect(self.finish)
    
    def start_reading(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_pressure)
        self.timer.start(self.period)  # 0.5Hz  

    def read_pressure(self):
        pressure = self.instrument.pressure_read()[0]
        self.pressureLineEdit.setText(pressure)
        
    def finish(self):
        print("worker_finished")
        self.pressureLineEdit.setText("")
        self.timer.stop()
        self.finished.emit()

            
        