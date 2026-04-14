import sys
from datetime import datetime
from zoneinfo import ZoneInfo
sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')


from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox
from PyQt5.QtCore import QTimer, Qt, QObject, pyqtSignal, QThread
from PyQt5 import uic

class magnetPowerSupply_widget(QWidget):
    def __init__(self, instrument):
        super().__init__()
        
        self.instrument = instrument
        
        uic.loadUi("GUI/ui_files/instrument_control_uis/Oxford_MercuryiPS_ui.ui", self)
        

        self.switchHeaterZbutton.setCheckable(True)
        self.switchHeaterZbutton.toggled.connect(self.switch_z_change_state)
        
    # [----------magnet power supply ui signals---------]
        
        self.switchHeaterZbutton.clicked.connect(self.switch_heater_power)
        self.targetFieldLimitSet.clicked.connect(self.set_target_field)
        self.targetFieldRead.clicked.connect(self.read_target_field)
        self.fieldRatingSet.clicked.connect(self.set_field_rate)
        self.fieldRatingRead.clicked.connect(self.read_field_rate)
        self.startDisplay.clicked.connect(self.magnetPowerSupply_thread) # [/]
    
    
    
    # [...........functions...........]
    
    def switch_heater_power(self):
        if self.switchHeaterZbutton.isChecked():
            self.instrument.set_switch_status('Z','ON')
        else:
            self.instrument.set_switch_status('Z','OFF')
    
    def set_switch_heater_status(self):

        switch_heater_status = self.instrument.read_all_switch_status()
        
        x_status = switch_heater_status['x'].split(':')[-1]
        y_status = switch_heater_status['y'].split(':')[-1]
        z_status = switch_heater_status['z'].split(':')[-1]
        
        print(x_status, y_status, z_status)
        
        if z_status == 'ON':
            self.on_state(self.switchHeaterZbutton)
        else:
            self.off_state(self.switchHeaterZbutton)
        
        self.switchHeaterZLineEdit.setText('')
        
    def set_target_field(self):
        value = self.targetFieldSpinBox.value()
        response = self.instrument.set_target_field('Z', str(value))
        print(response)
    
    def read_target_field(self):
        value = self.instrument.read_target_field('Z')
        print(value)
        self.targetFieldSpinBox.setValue(float(value))
        
    def set_field_rate(self):
        value = self.fieldRatingSpinBox.value()
        response = self.instrument.set_field_rate('Z', str(value))
        print(response)
    
    def read_field_rate(self):
        value = self.instrument.read_field_rate('Z')
        print(value)
        self.fieldRatingSpinBox.setValue(float(value))
        
    def off_state(self, button):
        
        button.setChecked(False)
        button.setText("OFF")
        button.setStyleSheet(
            "background-color: red; color: black"
        )
        
    def on_state(self, button):
        
        button.setChecked(True)
        button.setText("ON")
        button.setStyleSheet(
            "background-color: green; color: black"
        )
             
    def switch_z_change_state(self):
        
        if self.switchHeaterZbutton.isChecked():
            self.switchHeaterZbutton.setText("ON")
            self.switchHeaterZbutton.setStyleSheet(
                "background-color: green; color: black"
            )

        else:
            self.switchHeaterZbutton.setText("OFF")
            self.switchHeaterZbutton.setStyleSheet(
                "background-color: red; color: black"
            )
        
        now = datetime.now()
        now.strftime('%Y-%m-%d %H:%M:%S')
        self.switchHeaterZLineEdit.setText(str(now))
    
    def magnetPowerSupply_thread(self):
        print("magnet reading start")
        
        self.magnet_worker = magnetPowerSupply_worker(self.instrument, 1000, self.stopDisplay,
                                                     self.temperatureLineEdit,
                                                     self.currentLineEdit,
                                                     self.fieldZLineEdit)
        self.magnet_worker_thread = QThread()
        self.magnet_worker.moveToThread(self.magnet_worker_thread)
        
        self.magnet_worker_thread.started.connect(self.magnet_worker.start_reading)
        self.magnet_worker.finished.connect(self.magnet_worker_thread.quit)
        self.magnet_worker_thread.finished.connect(self.magnet_worker.deleteLater)
        self.magnet_worker_thread.finished.connect(self.magnet_worker_thread.deleteLater)
        
        self.magnet_worker_thread.start()
        
    # [/]

    

"""worker class for measuring magnetPowerSupply (thread)"""
class magnetPowerSupply_worker(QObject):
    finished = pyqtSignal()
    def __init__(self, instrument, period, magnetStopDisplayButton, temperatureLineEdit, currentLineEdit, fieldZLineEdit):
        super().__init__()
        
        self.instrument = instrument
        self.period = period
        self.magnetStopDisplayButton = magnetStopDisplayButton
        self.temperatureLineEdit = temperatureLineEdit
        self.currentLineEdit = currentLineEdit
        self.fieldZLineEdit = fieldZLineEdit
        
        self.magnetStopDisplayButton.clicked.connect(self.finish)
        
    def start_reading(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_magnetPowerSupply)
        self.timer.start(self.period)  # 1Hz  

    def read_magnetPowerSupply(self):
        temperature = self.instrument.read_temperature()
        current = self.instrument.read_current()[0]
        field = self.instrument.read_all_field()[0]
        
        self.temperatureLineEdit.setText(str(temperature))
        self.currentLineEdit.setText(str(current))
        self.fieldZLineEdit.setText(str(field))
        
    def finish(self):
        print("worker_finished")
        self.temperatureLineEdit.setText("")
        self.currentLineEdit.setText("")
        self.fieldZLineEdit.setText("")
        self.timer.stop()
        self.finished.emit()
        