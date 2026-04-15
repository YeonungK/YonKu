from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget
from PyQt5 import uic
from PyQt5.QtGui import QCloseEvent
import sys

import sys

sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')


class lockInAmplifier1_widget(QWidget):
    def __init__(self, instrument, device_info, device_key, parent):
        super().__init__()
        
        self.instrument = instrument
        self.data_list = device_info
        self.device_key = device_key
        self.parent = parent
        uic.loadUi("GUI/ui_files/instrument_control_uis/SRS_830_ui.ui", self)
        
        
    # [----------lock in amplifier ui output signals----------]

        # [######set buttons######]
        
        self.setAllButton.clicked.connect(self.set_all)
        
        # [REFERENCE AND PHASE]
        self.phaseSet.clicked.connect(self.phase_set)
        self.rsSet.clicked.connect(self.rs_set)
        self.rfSet.clicked.connect(self.rf_set)
        self.dhSet.clicked.connect(self.dh_set)
        self.ampSet.clicked.connect(self.amp_set) # [/]
        
        # [GAIN AND TIME CONSTANT]
        self.sensSet.clicked.connect(self.sens_set)
        self.reservSet.clicked.connect(self.reserv_set)
        self.timeCnstSet.clicked.connect(self.timeCnst_set)
        self.lpFilSet.clicked.connect(self.lpFil_set)
        self.syncFilSet.clicked.connect(self.syncFil_set) # [/]
        
        # [INPUT FILTER]
        self.inpConfSet.clicked.connect(self.inpConf_set)
        self.inputShiSet.clicked.connect(self.inputShi_set)
        self.inputCoupSet.clicked.connect(self.inputCoup_set)
        self.inputLnFilSet.clicked.connect(self.inputLnFil_set) # [/]
# [/]
        
        # [#######query buttons#######]
        
        self.qryAllButton.clicked.connect(self.query_all)
        
        # [REFERENCE AND PHASE]
        self.phaseQry.clicked.connect(self.phase_qry)
        self.rsQry.clicked.connect(self.rs_qry)
        self.rfQry.clicked.connect(self.rf_qry)
        self.dhQry.clicked.connect(self.dh_qry)
        self.ampQry.clicked.connect(self.amp_qry) # [/]
        
        # [GAIN AND TIME CONSTANT]
        self.sensQry.clicked.connect(self.sens_qry)
        self.reservQry.clicked.connect(self.reserv_qry)
        self.timeCnstQry.clicked.connect(self.timeCnst_qry)
        self.lpFilQry.clicked.connect(self.lpFil_qry)
        self.syncFilQry.clicked.connect(self.syncFil_qry) # [/]
        
        # [INPUT FILTER]
        self.inpConfQry.clicked.connect(self.inpConf_qry)
        self.inputShiQry.clicked.connect(self.inputShi_qry)
        self.inputCoupQry.clicked.connect(self.inputCoup_qry)
        self.inputLnFilQry.clicked.connect(self.inputLnFil_qry) # [/]
        # [/]
        # [/]
        
    
    # [...........functions...........]
    
    def initialize_widget(self):
        pass
    
    # [#######setting functions#######]
    
    def set_all(self):
        self.phase_set()
        self.rs_set()
        self.rf_set()
        self.dh_set()
        self.amp_set()
        self.sens_set()
        self.reserv_set()
        self.timeCnst_set()
        self.lpFil_set()
        self.syncFil_set()
        self.inpConf_set()
        self.inputShi_set()
        self.inputCoup_set()
        self.inputLnFil_set()
        
    # REFERENCE AND PHASE
    def phase_set(self):
        value = self.phaseLineEdit.text()
        try:
            value = float(value)
            self.instrument.set_phase(value)
            
        except:
            self.phaseLineEdit.setText("Type a valid input")

    def rs_set(self):
        value = self.rsComboBox.currentText()
        
        if value == "Internal":
            self.instrument.set_trigsource(1)
            self.rfLineEdit.setEnabled(True)
        else:
            self.instrument.set_trigsource(0)
            self.rfLineEdit.setEnabled(False)
            
    def rf_set(self):
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
    
    def dh_set(self):
        value = self.dhLineEdit.text()
        try:
            value = float(value)
            if value >= 1 and value <= 19999:
                self.instrument.set_harm(value)
            else:
                self.dhLineEdit.setText("Invalid input")
        except:
            self.dhLineEdit.setText("Invalid input")
    
    def amp_set(self):
        value = self.ampLineEdit.text()
        try:
            value = float(value)
            if value >= 0.004 and value <= 5:
                self.instrument.set_ampl(value)
            else:
                self.ampLineEdit.setText("Invalid input")
        except:
            self.ampLineEdit.setText("Invalid input")
            
    # GAIN AND TIME CONSTANT
    def sens_set(self):
        value = self.sensComboBox.currentText()
        
        try: 
            self.instrument.set_sens(self.instrument.sensset[value])
        except KeyError:
            print("can't find the key")
            
    def reserv_set(self):
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
                
    def timeCnst_set(self):
        value = self.timeCnstComboBox.currentText()
        
        try: 
            self.instrument.set_tau(self.instrument.tauset[value])
        except KeyError:
            print("can't find the key")          
        
    def lpFil_set(self):
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
    
    def syncFil_set(self):
        value = self.syncFilComboBox.currentText()
        
        match value:
            case "Off":
                self.instrument.set_sync(0)
            case "On":
                self.instrument.set_sync(1)
            case _:
                pass
    
    # INPUT FILTER
    def inpConf_set(self):
        value = self.inpConfComboBox.currentText()
        
        match value:
            case "A":
                self.instrument.set_input(0)
            case "B":
                self.instrument.set_input(1)
            case "I (1 M Ohms)":
                self.instrument.set_input(2)
            case "I (100 M Ohms)":
                self.instrument.set_input(3)
            case _:
                pass
    
    def inputShi_set(self):
        value = self.inputShiComboBox.currentText()
        
        match value:
            case "Float":
                self.instrument.set_ground(0)
            case "Ground":
                self.instrument.set_ground(1)
            case _:
                pass
    
    def inputCoup_set(self):
        value = self.inputCoupComboBox.currentText()
        
        match value:
            case "AC":
                self.instrument.set_couple(0)
            case "DC":
                self.instrument.set_couple(1)
            case _:
                pass
    
    def inputLnFil_set(self):
        value = self.inputLnFilComboBox.currentText()
        
        match value:
            case "Out / No Filters":
                self.instrument.set_filter(0)
            case "Line Notch":
                self.instrument.set_filter(1)
            case "2 x Line Notch":
                self.instrument.set_filter(2)
            case "Both Notch Filters":
                self.instrument.set_filter(3)
            case _:
                pass
     # [/]
    
    # [#######quering functions#######]
    
    def query_all(self):
        self.phase_qry()
        self.rs_qry()
        self.rf_qry()
        self.dh_qry()
        self.amp_qry()
        self.sens_qry()
        self.reserv_qry()
        self.timeCnst_qry()
        self.lpFil_qry()
        self.syncFil_qry()
        self.inpConf_qry()
        self.inputShi_qry()
        self.inputCoup_qry()
        self.inputLnFil_qry()
    
    # REFERENCE AND PHASE
    def phase_qry(self):
        value = str(self.instrument.get_phase())
        self.phaseLineEdit.setText(value)
        
    def rs_qry(self):
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
    
    def rf_qry(self):
        value = str(self.instrument.get_freq())
        self.rfLineEdit.setText(value)
        
    def dh_qry(self):
        value = str(self.instrument.get_harm())
        self.dhLineEdit.setText(value)
        
    def amp_qry(self):
        value = str(self.instrument.get_ampl())
        self.ampLineEdit.setText(value)
    
    # GAIN AND TIME CONSTANT
    def sens_qry(self):
        index = str(self.instrument.get_sens())
        print(index)
        
        value = list(self.instrument.sensset.keys())[int(index)]
        
        self.sensComboBox.setCurrentText(value)
        
    def reserv_qry(self):
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
            
    def timeCnst_qry(self):
        index = str(self.instrument.get_tau())
        print(index)
        
        value = list(self.instrument.tauset.keys())[int(index)]
        
        self.timeCnstComboBox.setCurrentText(value)
        
    def lpFil_qry(self):
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
            
    def syncFil_qry(self):
        value = str(self.instrument.get_sync())
        print(value)
        match value:
            case "0\n":
                print("0")
                self.rsComboBox.setCurrentText("Off")
            case "1\n":
                print("1")
                self.rsComboBox.setCurrentText("On")   
            case _:
                pass
    
    # INPUT FILTER
    def inpConf_qry(self):
        value = str(self.instrument.get_input())
        match value:
            case "0\n":
                print("0")
                self.rsComboBox.setCurrentText("A")
            case "1\n":
                print("1")
                self.rsComboBox.setCurrentText("B") 
            case "2\n":
                print("2")
                self.rsComboBox.setCurrentText("I (1 M Ohms)")
            case "3\n":
                print("3")
                self.rsComboBox.setCurrentText("I (100 M Ohms)")      
            case _:
                pass
            
    def inputShi_qry(self):
        value = str(self.instrument.get_ground())
        print(value)
        match value:
            case "0\n":
                print("0")
                self.rsComboBox.setCurrentText("Float")
            case "1\n":
                print("1")
                self.rsComboBox.setCurrentText("Ground")    
            case _:
                pass
            
    def inputCoup_qry(self):
        value = str(self.instrument.get_couple())
        print(value)
        match value:
            case "0\n":
                print("0")
                self.rsComboBox.setCurrentText("AC")
            case "1\n":
                print("1")
                self.rsComboBox.setCurrentText("DC")    
            case _:
                pass
            
    def inputLnFil_qry(self): 
        value = str(self.instrument.get_filter())
        match value: 
            case "0\n":
                print("0")
                self.rsComboBox.setCurrentText("Out / No Filters")
            case "1\n":
                print("1")
                self.rsComboBox.setCurrentText("Line Notch") 
            case "2\n":
                print("2")
                self.rsComboBox.setCurrentText("2 x Line Notch")
            case "3\n":
                print("3")
                self.rsComboBox.setCurrentText("Both Notch Filters")      
            case _:
                pass
   # [/] 
    # [/]
   
    def closeEvent(self, event: QCloseEvent):
        pass
        