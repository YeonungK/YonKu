from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget
from PyQt5 import uic
from PyQt5.QtGui import QCloseEvent
import sys

import sys

sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')


class lockInAmplifier2_widget(QWidget):
    def __init__(self, instrument):
        super().__init__()
        
        self.instrument = instrument
        
        uic.loadUi("GUI/ui_files/instrument_control_uis/SRS_830_ui.ui", self)
        
    # [----------lock in amplifier 2 ui output signals----------]

        # [######set buttons######]
        
        self.setAllButton.clicked.connect(self.set_all2)
        
        # [REFERENCE AND PHASE]
        self.phaseSet.clicked.connect(self.phase_set2)
        self.rsSet.clicked.connect(self.rs_set2)
        self.rfSet.clicked.connect(self.rf_set2)
        self.dhSet.clicked.connect(self.dh_set2) # [/]
        
        # [GAIN AND TIME CONSTANT]
        self.sensSet.clicked.connect(self.sens_set2)
        self.reservSet.clicked.connect(self.reserv_set2)
        self.timeCnstSet.clicked.connect(self.timeCnst_set2)
        self.lpFilSet.clicked.connect(self.lpFil_set2) # [/]
        
    # [/]
        
        # [#######query buttons#######]
        
        self.qryAllButton.clicked.connect(self.query_all2)
        
        # [REFERENCE AND PHASE]
        self.phaseQry.clicked.connect(self.phase_qry2)
        self.rsQry.clicked.connect(self.rs_qry2)
        self.rfQry.clicked.connect(self.rf_qry2)
        self.dhQry.clicked.connect(self.dh_qry2) # [/]
        
        # [GAIN AND TIME CONSTANT]
        self.sensQry.clicked.connect(self.sens_qry2)
        self.reservQry.clicked.connect(self.reserv_qry2)
        self.timeCnstQry.clicked.connect(self.timeCnst_qry2)
        self.lpFilQry.clicked.connect(self.lpFil_qry2) # [/]
        
        # [/]
    
        # [/]
   
        
    # [...........lock in amplifier 2...........]
    
    # [#######setting functions#######]
    
    def set_all2(self):
        self.phase_set2()
        self.rs_set2()
        self.rf_set2()
        self.dh_set2()
        self.sens_set2()
        self.reserv_set2()
        self.timeCnst_set2()
        self.lpFil_set2()
        
    # REFERENCE AND PHASE
    def phase_set2(self):
        value = self.phaseLineEdit.text()
        try:
            value = float(value)
            self.instrument.set_phase(value)
            
        except:
            self.phaseLineEdit.setText("Type a valid input")

    def rs_set2(self):
        value = self.rsComboBox.currentText()
        
        if value == "Internal":
            self.instrument.set_trigsource(1)
            self.rfLineEdit.setEnabled(True)
        else:
            self.instrument.set_trigsource(0)
            self.rfLineEdit.setEnabled(False)
            
    def rf_set2(self):
        value = self.rfLineEdit.text()
        try:
            value = float(value)
            
            if value > 200:
                self.syncFilComboBox.setEnabled(False)
            else:
                self.syncFilComboBox.setEnabled(True)
            self.instrument.set_freq(value)
            
        except:
            self.rfLineEdit.setText("Disabled / Invalid input")
    
    def dh_set2(self):
        value = self.dhLineEdit.text()
        try:
            value = float(value)
            if value >= 1 and value <= 19999:
                self.instrument.set_harm(value)
            else:
                self.dhLineEdit.setText("Invalid input")
        except:
            self.dhLineEdit.setText("Invalid input")
            
    # GAIN AND TIME CONSTANT
    def sens_set2(self):
        value = self.sensComboBox.currentText()
        
        try: 
            self.instrument.set_sens(self.instrument.sensset[value])
        except KeyError:
            print("can't find the key")
            
    def reserv_set2(self):
        value = self.reservComboBox.currentText()
        
        match value:
            case "High Reserve":
                self.instrument.set_reserve(0)
            case "Normal":
                self.instrument.set_reserve(1)
            case "Low Noise":
                self.instrument.set_reserve(2)
            case _:
                pass
                
    def timeCnst_set2(self):
        value = self.timeCnstComboBox.currentText()
        
        try: 
            self.instrument.set_tau(self.instrument.tauset[value])
        except KeyError:
            print("can't find the key")          
        
    def lpFil_set2(self):
        value = self.lpFilComboBox.currentText()
        
        match value:
            case "6":
                self.instrument.set_slope(0)
            case "12":
                self.instrument.set_slope(1)
            case "18":
                self.instrument.set_slope(2)
            case "24":
                self.instrument.set_slope(3)
            case _:
                pass
    
    # [/]
    
    # [#######quering functions#######]
    
    def query_all2(self):
        self.phase_qry()
        self.rs_qry()
        self.rf_qry()
        self.dh_qry()
        self.sens_qry()
        self.reserv_qry()
        self.timeCnst_qry()
        self.lpFil_qry()
    
    # REFERENCE AND PHASE
    def phase_qry2(self):
        value = str(self.instrument.get_phase())
        self.phaseLineEdit.setText(value)
        
    def rs_qry2(self):
        value = str(self.instrument.get_trigsource())
        print(value)
        match value:
            case "0\n":
                print("0")
                self.rsComboBox.setCurrentText("External")
            case "1\n":
                print("1")
                self.rsComboBox.setCurrentText("Internal")   
            case _:
                pass
    
    def rf_qry2(self):
        value = str(self.instrument.get_freq())
        self.rfLineEdit.setText(value)
        
    def dh_qry2(self):
        value = str(self.instrument.get_harm())
        self.dhLineEdit.setText(value)
        
    # GAIN AND TIME CONSTANT
    def sens_qry2(self):
        index = str(self.instrument.get_sens())
        print(index)
        
        value = list(self.instrument.sensset.keys())[int(index)]
        
        self.sensComboBox.setCurrentText(value)
        
    def reserv_qry2(self):
        value = str(self.instrument.get_reserve())
        print(value)
        match value:
            case "0\n":
                print("0")
                self.rsComboBox.setCurrentText("High Reserve")
            case "1\n":
                print("1")
                self.rsComboBox.setCurrentText("Normal") 
            case "2\n":
                print("2")
                self.rsComboBox.setCurrentText("Low Noise")   
            case _:
                pass
            
    def timeCnst_qry2(self):
        index = str(self.instrument.get_tau())
        print(index)
        
        value = list(self.instrument.tauset.keys())[int(index)]
        
        self.timeCnstComboBox.setCurrentText(value)
        
    def lpFil_qry2(self):
        value = str(self.instrument.get_slope())
        print(value)
        match value:
            case "0\n":
                print("0")
                self.rsComboBox.setCurrentText("6")
            case "1\n":
                print("1")
                self.rsComboBox.setCurrentText("12") 
            case "2\n":
                print("2")
                self.rsComboBox.setCurrentText("18")
            case "3\n":
                print("3")
                self.rsComboBox.setCurrentText("24")      
            case _:
                pass
            

    # [/]
# [/]
   
        
    def closeEvent(self, event: QCloseEvent):
        pass
        