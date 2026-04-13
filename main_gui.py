import sys
import re
import keyword
import time
import os
import glob
import threading
import traceback
import importlib
from pathlib import Path
from functools import partial

from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget, QMessageBox, QAction, QLineEdit, QComboBox
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, QTimer, Qt, QSize
from PyQt5.QtGui import QCloseEvent
from PyQt5 import uic

from GUI import ChsBigLineUi as chs, NewPlotSettingUi as nps, OpenPlotSettingUi as ops, PlotUi, ExperimentSettingUi as esu
from GUI import SerialInstCreateUi as sic, GpibInstCreateUi as gic, EthernetInstCreateUi as eic, USB6525InstCreateUi as bic, DisconnectedDevicesUi as ddu
from GUI import DeviceListUi as dlu, SerialInstDeviceUi as sidu, GpibInstDeviceUi as gidu, EthernetInstDeviceUi as eidu, USB6525InstDeviceUi as uidu
from Tools import LakeShore_336, INFICON_VGC401, GasValve, SRS_830, Oxford_MercuryiPS, DataLogger, Dataset, NewQMdiSubWindow


from datetime import datetime
from zoneinfo import ZoneInfo




"""Exception Handler"""
class ExceptionForwarder(QObject):
    exception_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def handle_exception(self, exc_type, exc_value, exc_tb):
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        print(error_msg)
        self.exception_occurred.emit(error_msg)

# not used
class PlotUpdateWorker(QObject):
    finished = pyqtSignal()
    def __init__(self, plot_widgets, dataset, pausePushButton):
        
        super().__init__()
         
        self.plot_widgets = plot_widgets
        self.dataset = dataset
        self.pausePushButton = pausePushButton
        
    def start_plot_update(self):
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.plot_update)
        self.timer.start(2000)  # 1Hz
    
    def plot_update(self):
        for index, plt_wid in self.plot_widgets.items():
            if isinstance(plt_wid, PlotUi.plotWidget):
                plt_wid.plot_data()
    
    def pause_resume_experiment(self):
        if self.pausePushButton.isChecked():
            self.timer.stop()
        else:
            self.timer = QTimer()
            self.timer.timeout.connect(self.plot_update)
            self.timer.start(2000) 
    
    def end_experiment(self):
        self.timer.stop()
        
        print("plot_update_worker_finished")
        
        self.finished.emit()
            
"""worker class for Expriments and Real-time Plotting (thread)"""
class PlotWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal()
    update = pyqtSignal()

    def __init__(self, instruments, plot_widgets, dataset, period, pausePushButton, 
                 titleLineEdit, xLineEdit, yLineEdit, rLineEdit, thetaLineEdit,
                 xLineEdit2, yLineEdit2, rLineEdit2, thetaLineEdit2, 
                 chALineEdit, chBLineEdit, chCLineEdit, chDLineEdit,
                 chABigLine, chBBigLine, chCBigLine, chDBigLine, unitButton,
                 magnetzLineEdit, currentLineEdit, experimentSettingWid):
        
        super().__init__()
        
        self.instruments = instruments
        self.omitted_instruments = []
        for device_model, instrument in self.instruments.items():
            if not instrument.data_type:
                self.omitted_instruments.append(device_model)
            if device_model == "INFICON_VGC401":
                self.omitted_instruments.append(device_model)
        
        for device_model in self.omitted_instruments:
            del self.instruments[device_model]
        print(self.instruments)
        
        self.plot_widgets = plot_widgets
        self.period = period
        self.pausePushButton = pausePushButton
        self.titleLineEdit = titleLineEdit
        self.dataset = dataset
        self.xLineEdit = xLineEdit
        self.yLineEdit = yLineEdit
        self.rLineEdit = rLineEdit
        self.thetaLineEdit = thetaLineEdit
        self.xLineEdit2 = xLineEdit2
        self.yLineEdit2 = yLineEdit2
        self.rLineEdit2 = rLineEdit2
        self.thetaLineEdit2 = thetaLineEdit2
        self.chALineEdit = chALineEdit
        self.chBLineEdit = chBLineEdit
        self.chCLineEdit = chCLineEdit
        self.chDLineEdit = chDLineEdit
        self.chABigLine = chABigLine
        self.chBBigLine = chBBigLine
        self.chCBigLine = chCBigLine
        self.chDBigLine = chDBigLine
        self.unitButton = unitButton
        self.magnetzLineEdit = magnetzLineEdit
        self.currentLineEdit = currentLineEdit
        self.experimentSettingWid = experimentSettingWid
    
        
    def start_experiment(self):

        self.timer = QTimer()
        self.timer.timeout.connect(self.plot_update)
        self.timer.start(self.period)  # 1Hz
        
        
        self.experiment_datetime = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
        self.experiment_name = self.titleLineEdit.text()
        self.experiment_title = self.experiment_datetime + "_" + self.experiment_name
        self.logger = DataLogger.DataLogger(self.instruments, self.dataset, self.experiment_title)
        
        self.log_experiment_parameters()
        
    def log_experiment_parameters(self):

        self.file_path = Path(f"C:/Users/szkop/OneDrive/Desktop/YonKu/Data/experiment_parameters/{self.experiment_title}.txt")
        self.experimentSettingWid.save_all_values()
        
        self.experiment_parameters = f"""startDatetime:{self.experiment_datetime}
name:{self.experiment_name}
measurementPeriod:{self.period}


temperature_ch_A_name:{self.experimentSettingWid.experiment_parameters['temperature_name']['ch_A']}
temperature_ch_B_name:{self.experimentSettingWid.experiment_parameters['temperature_name']['ch_B']}
temperature_ch_C_name:{self.experimentSettingWid.experiment_parameters['temperature_name']['ch_C']}
temperature_ch_D_name:{self.experimentSettingWid.experiment_parameters['temperature_name']['ch_D']}

temperature_ch_A_unit:{self.experimentSettingWid.experiment_parameters['temperature_unit']['ch_A']}
temperature_ch_B_unit:{self.experimentSettingWid.experiment_parameters['temperature_unit']['ch_B']}
temperature_ch_C_unit:{self.experimentSettingWid.experiment_parameters['temperature_unit']['ch_C']}
temperature_ch_D_unit:{self.experimentSettingWid.experiment_parameters['temperature_unit']['ch_D']}


resistance_ch_A_name:{self.experimentSettingWid.experiment_parameters['resistance_name']['ch_A']}
resistance_ch_B_name:{self.experimentSettingWid.experiment_parameters['resistance_name']['ch_B']}
resistance_ch_C_name:{self.experimentSettingWid.experiment_parameters['resistance_name']['ch_C']}
resistance_ch_D_name:{self.experimentSettingWid.experiment_parameters['resistance_name']['ch_D']}

resistance_ch_A_unit:{self.experimentSettingWid.experiment_parameters['resistance_unit']['ch_A']}
resistance_ch_B_unit:{self.experimentSettingWid.experiment_parameters['resistance_unit']['ch_B']}
resistance_ch_C_unit:{self.experimentSettingWid.experiment_parameters['resistance_unit']['ch_C']}
resistance_ch_D_unit:{self.experimentSettingWid.experiment_parameters['resistance_unit']['ch_D']}


lockIn_x_name:{self.experimentSettingWid.experiment_parameters['lockIn_name']['x']}
lockIn_y_name:{self.experimentSettingWid.experiment_parameters['lockIn_name']['y']}
lockIn_r_name:{self.experimentSettingWid.experiment_parameters['lockIn_name']['r']}
lockIn_theta_name:{self.experimentSettingWid.experiment_parameters['lockIn_name']['theta']}

lockIn_x_unit:{self.experimentSettingWid.experiment_parameters['lockIn_unit']['x']}
lockIn_y_unit:{self.experimentSettingWid.experiment_parameters['lockIn_unit']['y']}
lockIn_r_unit:{self.experimentSettingWid.experiment_parameters['lockIn_unit']['r']}
lockIn_theta_unit:{self.experimentSettingWid.experiment_parameters['lockIn_unit']['theta']}


lockIn2_x_name:{self.experimentSettingWid.experiment_parameters['lockIn2_name']['x']}
lockIn2_y_name:{self.experimentSettingWid.experiment_parameters['lockIn2_name']['y']}
lockIn2_r_name:{self.experimentSettingWid.experiment_parameters['lockIn2_name']['r']}
lockIn2_theta_name:{self.experimentSettingWid.experiment_parameters['lockIn2_name']['theta']}

lockIn2_x_unit:{self.experimentSettingWid.experiment_parameters['lockIn2_unit']['x']}
lockIn2_y_unit:{self.experimentSettingWid.experiment_parameters['lockIn2_unit']['y']}
lockIn2_r_unit:{self.experimentSettingWid.experiment_parameters['lockIn2_unit']['r']}
lockIn2_theta_unit:{self.experimentSettingWid.experiment_parameters['lockIn2_unit']['theta']}


field_name:{self.experimentSettingWid.experiment_parameters['field_name']['field']}
field_unit:{self.experimentSettingWid.experiment_parameters['field_unit']['field']}


current_name:{self.experimentSettingWid.experiment_parameters['current_name']['current']}
current_unit:{self.experimentSettingWid.experiment_parameters['current_unit']['current']}


time_name:{self.experimentSettingWid.experiment_parameters['time_name']['time']}

{list(self.instruments.keys())}\n"""
        
        
        with open(self.file_path, "w") as f:
            f.write(self.experiment_parameters)
            f.close()
    

            
    def plot_update(self):
    
        self.instrument_read_data()
        
        self.update.emit()
        
        # for index, plt_wid in self.plot_widgets.items():
        #     if isinstance(plt_wid, PlotUi.plotWidget):
        #         plt_wid.plot_data()
    
    def instrument_read_data(self):
        
        self.logging_data_list = []
        
        for device_model, instrument in self.instruments.items():
            for data_type, function in instrument.data_function.items():
                data_list = setattr(self, f"{data_type}_list", function())
                data_list = getattr(self, f"{data_type}_list")
                print(data_list)
                self.logging_data_list.append(data_list)
                index = 0
                for data_ch in instrument.data_type[data_type]:
                    self.dataset[data_type][data_ch].append(data_list[index])
                    index += 1

                if data_type == 'temperature':
                    if self.unitButton.isChecked():
                        self.chALineEdit.setText(str(data_list[0]))
                        self.chBLineEdit.setText(str(data_list[1]))
                        self.chCLineEdit.setText(str(data_list[2]))
                        self.chDLineEdit.setText(str(data_list[3]))
                        
                        self.chABigLine.setText(str(data_list[0]))
                        self.chBBigLine.setText(str(data_list[1]))
                        self.chCBigLine.setText(str(data_list[2]))
                        self.chDBigLine.setText(str(data_list[3]))
                    else:
                        self.chALineEdit.setText(str(data_list[0]))
                        self.chBLineEdit.setText(str(data_list[1]))
                        self.chCLineEdit.setText(str(data_list[2]))
                        self.chDLineEdit.setText(str(data_list[3]))
                        
                        self.chABigLine.setText(str(data_list[0]))
                        self.chBBigLine.setText(str(data_list[1]))
                        self.chCBigLine.setText(str(data_list[2]))
                        self.chDBigLine.setText(str(data_list[3]))
                
                if data_type == 'lockIn':
                    self.xLineEdit.setText(str(data_list[0]))
                    self.yLineEdit.setText(str(data_list[1]))
                    self.rLineEdit.setText(str(data_list[2]))
                    self.thetaLineEdit.setText(str(data_list[3]))
                
                if data_type == 'lockIn2':
                    self.xLineEdit2.setText(str(data_list[0]))
                    self.yLineEdit2.setText(str(data_list[1]))
                    self.rLineEdit2.setText(str(data_list[2]))
                    self.thetaLineEdit2.setText(str(data_list[3]))
            
            
        now = datetime.now(ZoneInfo('America/New_York')).timestamp()
        self.dataset['time']['time'].append(now)
        
        self.logging_data_list.append(now)   
        self.logger.append(self.logging_data_list)     
            
        
                    
        
        
                
        # temp_list = self.instruments['Lakeshore_336'].temp_read_all()
        # resist_list = self.instruments['Lakeshore_336'].resist_read_all()
        # lockIn_list = self.instruments['SRS_830'].get_all()
        # lockIn2_list = self.instruments['SRS_830_2'].get_all()
        # field_list = self.instruments['Oxford_MercuryiPS'].read_all_field()
        # current_list = self.instruments['Oxford_MercuryiPS'].read_current()
        
        
        # self.dataset['temperature']['ch_A'].append(temp_list[0])
        # self.dataset['temperature']['ch_B'].append(temp_list[1])
        # self.dataset['temperature']['ch_C'].append(temp_list[2])
        # self.dataset['temperature']['ch_D'].append(temp_list[3])
        
        # if self.unitButton.isChecked():
        #     self.chALineEdit.setText(str(temp_list[0]))
        #     self.chBLineEdit.setText(str(temp_list[1]))
        #     self.chCLineEdit.setText(str(temp_list[2]))
        #     self.chDLineEdit.setText(str(temp_list[3]))
            
        #     self.chABigLine.setText(str(temp_list[0]))
        #     self.chBBigLine.setText(str(temp_list[1]))
        #     self.chCBigLine.setText(str(temp_list[2]))
        #     self.chDBigLine.setText(str(temp_list[3]))
            
        # else:
        #     self.chALineEdit.setText(str(resist_list[0]))
        #     self.chBLineEdit.setText(str(resist_list[1]))
        #     self.chCLineEdit.setText(str(resist_list[2]))
        #     self.chDLineEdit.setText(str(resist_list[3]))
            
        #     self.chABigLine.setText(str(resist_list[0]))
        #     self.chBBigLine.setText(str(resist_list[1]))
        #     self.chCBigLine.setText(str(resist_list[2]))
        #     self.chDBigLine.setText(str(resist_list[3]))
        
        # self.dataset['resistance']['ch_A'].append(resist_list[0])
        # self.dataset['resistance']['ch_B'].append(resist_list[1])
        # self.dataset['resistance']['ch_C'].append(resist_list[2])
        # self.dataset['resistance']['ch_D'].append(resist_list[3])
        
        # self.dataset['lockIn']['x'].append(lockIn_list[0])
        # self.dataset['lockIn']['y'].append(lockIn_list[1])
        # self.dataset['lockIn']['r'].append(lockIn_list[2])
        # self.dataset['lockIn']['theta'].append(lockIn_list[3])
        
        # self.dataset['lockIn2']['x'].append(lockIn2_list[0])
        # self.dataset['lockIn2']['y'].append(lockIn2_list[1])
        # self.dataset['lockIn2']['r'].append(lockIn2_list[2])
        # self.dataset['lockIn2']['theta'].append(lockIn2_list[3])
        
        
        # self.xLineEdit.setText(str(lockIn_list[0]))
        # self.yLineEdit.setText(str(lockIn_list[1]))
        # self.rLineEdit.setText(str(lockIn_list[2]))
        # self.thetaLineEdit.setText(str(lockIn_list[3]))
        
        # self.xLineEdit2.setText(str(lockIn2_list[0]))
        # self.yLineEdit2.setText(str(lockIn2_list[1]))
        # self.rLineEdit2.setText(str(lockIn2_list[2]))
        # self.thetaLineEdit2.setText(str(lockIn2_list[3]))
        
        # self.dataset['field']['field'].append(field_list)
        

        # self.magnetzLineEdit.setText(str(field_list))
        
        # if not current_list == None:
        #     self.dataset['current']['current'].append(current_list)
            
        #     self.currentLineEdit.setText(str(current_list))
        
        # else:
        #     pass

        
        # self.dataset['time']['time'].append(now)
        # self.logger.append(temp_list, resist_list, lockIn_list, lockIn2_list, field_list, current_list, now)
    
        
    def pause_resume_experiment(self):
        if self.pausePushButton.isChecked():
            self.timer.stop()
            pauseTime = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
            with open(self.file_path, "a") as f:
                f.write(f"\n\npauseDatetime: {pauseTime}")
                f.close()
        else:
            resumeTime = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
            with open(self.file_path, "a") as f:
                f.write(f"\nresumeDatetime: {resumeTime}")
                f.close()
            self.timer = QTimer()
            self.timer.timeout.connect(self.plot_update)
            self.timer.start(self.period) 
    
    def end_experiment(self):
        self.timer.stop()
        
        endTime = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
        with open(self.file_path, "a") as f:
            f.write(f"\n\nendDatetime: {endTime}")
            f.close() 
        
        self.chALineEdit.setText("")
        self.chBLineEdit.setText("")
        self.chCLineEdit.setText("")
        self.chDLineEdit.setText("")
        
        self.chABigLine.setText("")
        self.chBBigLine.setText("")
        self.chCBigLine.setText("")
        self.chDBigLine.setText("")
        
        print("worker_finished")
        
        self.finished.emit()
        
"""worker class for measuring pressureGauge (thread)"""
class PressureWorker(QObject):
    finished = pyqtSignal()
    def __init__(self, pressureDevice, period, stopDisplayButton, pressureLineEdit):
        super().__init__()
        
        self.pressureDevice = pressureDevice
        self.period = period
        self.stopDisplayButton = stopDisplayButton
        self.pressureLineEdit = pressureLineEdit
        
        self.stopDisplayButton.clicked.connect(self.finish)
    
    def start_reading(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_pressure)
        self.timer.start(self.period)  # 0.5Hz  

    def read_pressure(self):
        pressure = self.pressureDevice.pressure_read()[0]
        self.pressureLineEdit.setText(pressure)
        
    def finish(self):
        print("worker_finished")
        self.pressureLineEdit.setText("")
        self.timer.stop()
        self.finished.emit()

"""worker class for measuring magnetPowerSupply (thread)"""
class MagnetPowerSupplyWorker(QObject):
    finished = pyqtSignal()
    def __init__(self, magnetDevice, period, magnetStopDisplayButton, temperatureLineEdit, currentLineEdit, fieldZLineEdit):
        super().__init__()
        
        self.magnetDevice = magnetDevice
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
        temperature = self.magnetDevice.read_temperature()
        current = self.magnetDevice.read_current()[0]
        field = self.magnetDevice.read_all_field()[0]
        
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
        
        
"""main gui window class"""
class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        
        # [Error log creation & Error Centralization]
        
        now = datetime.now()
        self.error_log_title = now.strftime("%Y-%m-%d--%H-%M-%S")
        self.error_log_heading = "Szkopek Lab Error Log Book - " + self.error_log_title
        self.error_logger = DataLogger.ErrorLogger(self.error_log_heading, self.error_log_title) 
        
        self.exception_forwarder = ExceptionForwarder()
        sys.excepthook = self.exception_forwarder.handle_exception
        self.exception_forwarder.exception_occurred.connect(self.show_error_in_main_thread) # [/]
        
        # [System Setup]
        
        uic.loadUi("GUI/ui_files/graphene.ui", self)
        self.mdi = self.mdiArea_2
        self.mdi_plot = self.mdiArea
        
        self._initial_mdi_size = None
        self._initial_sub_sizes = {}
        
        self.instrument_wid = {}
        self.instruments = {}  # self.instruments = {'model_name' : self.instrument}
        self.devices = {}
        self.device_count = 0

        self.plot_widgets = {}
        self.plot_widget_count = 0
        
        
        # [Instruments & Widgets & Signals]
        
        # [=========instruments=========]
        
        self.instruments_setup()  # connect and query identifications from each instrument
        self.dataset_setup() # make an empty dataset according to the instruments used for this system # [/]
             
        # [==========widgets==========]
        
        self.add_windows() 
        self.connect_instrument_windows()  # [/]
       
        # [=======graphene ui menu signals=======]

        # [menu bar - PLOT]
        self.action_Add_Plot_Window.triggered.connect(self.new_plot_setting)
        self.action_Open_Old_Plot.triggered.connect(self.open_plot_setting) # [/]
        
        # [menu bar - VIEW]
        
        for device_key, data_list in self.devices.items():
            device_name = data_list["name"]

            # Retrieve dynamic attributes
            action = getattr(self, f"action_{device_name}", None)
            subwindow = getattr(self, f"{device_name}Sub", None)
            view_func = getattr(self, f"{device_name}Sub_view", None)

            # Ensure all exist before connecting
            if not all([action, subwindow, view_func]):
                print(f"Warning: Missing attributes for device '{device_name}'. Skipping connection.")
                continue

            # Set the checked state based on subwindow visibility
            action.setChecked(not subwindow.isHidden())

            # Connect the QAction’s triggered signal to the toggle function
            action.triggered.connect(view_func)
        # [/]
        
        # [menu bar - DEVICE]
        
        self.actionSerial_Instrument.triggered.connect(self.serial_instrument_create)
        self.actionGPIB_Instrument.triggered.connect(self.gpib_instrument_create)
        self.actionEthernet_Instrument.triggered.connect(self.ethernet_instrument_create)
        self.actionUSB_Instrument.triggered.connect(self.usb_6525_instrument_create)
        self.actionDeviceList.triggered.connect(self.device_list_show) # [/]
        
        # [menu bar - EXPERIMENT]
        
        self.actionEdit_channel_name.triggered.connect(self.experiment_setting_create)# [/]
        
        # [main - EXPERIMENT]
        
        self.startPushButton.clicked.connect(self.check_experiment_condition)
        self.pausePushButton.clicked.connect(self.pause_resume_experiment_thread)
        self.endAndSavePushButton.clicked.connect(self.end_experiment_worker) 
        
        self.pausePushButton.setEnabled(False)
        self.pausePushButton.setCheckable(True)
        self.startPushButton.setCheckable(False)
        self.startPushButton.setEnabled(True)
        self.endAndSavePushButton.setEnabled(False)
        
        
        # [/]
        # [/]

        # [======instrument ui output signals======]
        
        # [----------lock in amplifier ui output signals----------]

        # [######set buttons######]
        
        self.lockInAmplifier1Wid.setAllButton.clicked.connect(self.set_all)
        
        # [REFERENCE AND PHASE]
        self.lockInAmplifier1Wid.phaseSet.clicked.connect(self.phase_set)
        self.lockInAmplifier1Wid.rsSet.clicked.connect(self.rs_set)
        self.lockInAmplifier1Wid.rfSet.clicked.connect(self.rf_set)
        self.lockInAmplifier1Wid.dhSet.clicked.connect(self.dh_set)
        self.lockInAmplifier1Wid.ampSet.clicked.connect(self.amp_set) # [/]
        
        # [GAIN AND TIME CONSTANT]
        self.lockInAmplifier1Wid.sensSet.clicked.connect(self.sens_set)
        self.lockInAmplifier1Wid.reservSet.clicked.connect(self.reserv_set)
        self.lockInAmplifier1Wid.timeCnstSet.clicked.connect(self.timeCnst_set)
        self.lockInAmplifier1Wid.lpFilSet.clicked.connect(self.lpFil_set)
        self.lockInAmplifier1Wid.syncFilSet.clicked.connect(self.syncFil_set) # [/]
        
        # [INPUT FILTER]
        self.lockInAmplifier1Wid.inpConfSet.clicked.connect(self.inpConf_set)
        self.lockInAmplifier1Wid.inputShiSet.clicked.connect(self.inputShi_set)
        self.lockInAmplifier1Wid.inputCoupSet.clicked.connect(self.inputCoup_set)
        self.lockInAmplifier1Wid.inputLnFilSet.clicked.connect(self.inputLnFil_set) # [/]
# [/]
        
        # [#######query buttons#######]
        
        self.lockInAmplifier1Wid.qryAllButton.clicked.connect(self.query_all)
        
        # [REFERENCE AND PHASE]
        self.lockInAmplifier1Wid.phaseQry.clicked.connect(self.phase_qry)
        self.lockInAmplifier1Wid.rsQry.clicked.connect(self.rs_qry)
        self.lockInAmplifier1Wid.rfQry.clicked.connect(self.rf_qry)
        self.lockInAmplifier1Wid.dhQry.clicked.connect(self.dh_qry)
        self.lockInAmplifier1Wid.ampQry.clicked.connect(self.amp_qry) # [/]
        
        # [GAIN AND TIME CONSTANT]
        self.lockInAmplifier1Wid.sensQry.clicked.connect(self.sens_qry)
        self.lockInAmplifier1Wid.reservQry.clicked.connect(self.reserv_qry)
        self.lockInAmplifier1Wid.timeCnstQry.clicked.connect(self.timeCnst_qry)
        self.lockInAmplifier1Wid.lpFilQry.clicked.connect(self.lpFil_qry)
        self.lockInAmplifier1Wid.syncFilQry.clicked.connect(self.syncFil_qry) # [/]
        
        # [INPUT FILTER]
        self.lockInAmplifier1Wid.inpConfQry.clicked.connect(self.inpConf_qry)
        self.lockInAmplifier1Wid.inputShiQry.clicked.connect(self.inputShi_qry)
        self.lockInAmplifier1Wid.inputCoupQry.clicked.connect(self.inputCoup_qry)
        self.lockInAmplifier1Wid.inputLnFilQry.clicked.connect(self.inputLnFil_qry) # [/]
# [/]
 # [/]
        
        # [----------lock in amplifier 2 ui output signals----------]

        # [######set buttons######]
        
        self.lockInAmplifier2Wid.setAllButton.clicked.connect(self.set_all2)
        
        # [REFERENCE AND PHASE]
        self.lockInAmplifier2Wid.phaseSet.clicked.connect(self.phase_set2)
        self.lockInAmplifier2Wid.rsSet.clicked.connect(self.rs_set2)
        self.lockInAmplifier2Wid.rfSet.clicked.connect(self.rf_set2)
        self.lockInAmplifier2Wid.dhSet.clicked.connect(self.dh_set2) # [/]
        
        # [GAIN AND TIME CONSTANT]
        self.lockInAmplifier2Wid.sensSet.clicked.connect(self.sens_set2)
        self.lockInAmplifier2Wid.reservSet.clicked.connect(self.reserv_set2)
        self.lockInAmplifier2Wid.timeCnstSet.clicked.connect(self.timeCnst_set2)
        self.lockInAmplifier2Wid.lpFilSet.clicked.connect(self.lpFil_set2) # [/]
        
# [/]
        
        # [#######query buttons#######]
        
        self.lockInAmplifier2Wid.qryAllButton.clicked.connect(self.query_all2)
        
        # [REFERENCE AND PHASE]
        self.lockInAmplifier2Wid.phaseQry.clicked.connect(self.phase_qry2)
        self.lockInAmplifier2Wid.rsQry.clicked.connect(self.rs_qry2)
        self.lockInAmplifier2Wid.rfQry.clicked.connect(self.rf_qry2)
        self.lockInAmplifier2Wid.dhQry.clicked.connect(self.dh_qry2) # [/]
        
        # [GAIN AND TIME CONSTANT]
        self.lockInAmplifier2Wid.sensQry.clicked.connect(self.sens_qry2)
        self.lockInAmplifier2Wid.reservQry.clicked.connect(self.reserv_qry2)
        self.lockInAmplifier2Wid.timeCnstQry.clicked.connect(self.timeCnst_qry2)
        self.lockInAmplifier2Wid.lpFilQry.clicked.connect(self.lpFil_qry2) # [/]
        
# [/]
 # [/]
        
        # [---------temperature controller ui output signals---------]
        
        self.temperatureControllerWid.chAExpandButton.clicked.connect(self.expand_chA_line)
        self.temperatureControllerWid.chBExpandButton.clicked.connect(self.expand_chB_line)
        self.temperatureControllerWid.chCExpandButton.clicked.connect(self.expand_chC_line)
        self.temperatureControllerWid.chDExpandButton.clicked.connect(self.expand_chD_line) # [/]
        
        # [---------pressure gauge ui output signals---------]
        
        self.pressureGaugeWid.startDisplay.clicked.connect(self.pressureGauge_thread) # [/]
        
        # [----------gas valve and pressure gauge ui signals---------]
        
        self.gasValveWid.pumpPushButton.toggled.connect(self.pump_change)
        self.gasValveWid.ivcPushButton.toggled.connect(self.ivc_change)
        self.gasValveWid.hePushButton.toggled.connect(self.he_change)
        self.gasValveWid.allOffPushButton.clicked.connect(self.gas_all_off)
        self.gasValveWid.allOnPushButton.clicked.connect(self.gas_all_on) # [/]
        
        # [----------magnet power supply ui signals---------]
        
        self.magnetPowerSupplyWid.switchHeaterZbutton.clicked.connect(self.switch_heater_power)
        # self.magnetPowerSupplyWid.currentLimitSet.clicked.connect(self.current_lim_set)
        # self.magnetPowerSupplyWid.currentLimitRead.clicked.connect(self.current_lim_read)
        self.magnetPowerSupplyWid.targetFieldLimitSet.clicked.connect(self.set_target_field)
        self.magnetPowerSupplyWid.targetFieldRead.clicked.connect(self.read_target_field)
        self.magnetPowerSupplyWid.fieldRatingSet.clicked.connect(self.set_field_rate)
        self.magnetPowerSupplyWid.fieldRatingRead.clicked.connect(self.read_field_rate)
        self.magnetPowerSupplyWid.startDisplay.clicked.connect(self.magnetPowerSupply_thread)

# [/]
        
         # [/]
         # [/]
        
        self.showMaximized()
        self.show()  # [/]
        

    # [Functions]

    def sanitize_name(self, name: str) -> str:
        clean = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in str(name))
        if not clean:
            clean = "unnamed"
        if clean[0].isdigit():
            clean = "_" + clean
        return clean

    def bind_dynamic_signals(self):
        """
        Automatically connect every read/write button using self.ui_definition.
        """
        for category_name, components in self.ui_definition.items():
            safe_category = self.sanitize_name(category_name)

            for component in components:
                component_name = component.get("name", "component")
                safe_component = self.sanitize_name(component_name)
                base = f"{safe_category}_{safe_component}"

                # Read button
                if component.get("read", False):
                    read_button = self.findChild(QPushButton, f"{base}_readButton")
                    if read_button is not None:
                        read_button.clicked.connect(
                            partial(self.handle_read, category_name, component)
                        )

                # Write button
                if component.get("write", False):
                    write_button = self.findChild(QPushButton, f"{base}_writeButton")
                    if write_button is not None:
                        write_button.clicked.connect(
                            partial(self.handle_write, category_name, component)
                        )

    def get_component_widget(self, category_name: str, component: dict):
        """
        Find the main input widget for a component.
        Returns either QLineEdit, QComboBox, or None.
        """
        safe_category = self.sanitize_name(category_name)
        safe_component = self.sanitize_name(component.get("name", "component"))
        base = f"{safe_category}_{safe_component}"

        comp_type = component.get("type", 1)

        if comp_type == 1:
            return self.findChild(QLineEdit, f"{base}_lineEdit")
        if comp_type == 2:
            return self.findChild(QComboBox, f"{base}_comboBox")

        return self.findChild(QLineEdit, f"{base}_lineEdit")
    def handle_read(self, category_name: str, component: dict):
        """
        Called when a Read button is pressed.
        Reads from the instrument and updates the UI widget.
        """
        widget = self.get_component_widget(category_name, component)
        command = component.get("command", "")

        if widget is None:
            print(f"Read failed: widget not found for {category_name} / {component.get('name')}")
            return

        try:
            # Replace this with your real instrument read/query logic
            value = self.instrument.query(command)

            if isinstance(widget, QLineEdit):
                widget.setText(str(value))

            elif isinstance(widget, QComboBox):
                text_value = str(value)
                index = widget.findText(text_value)
                if index >= 0:
                    widget.setCurrentIndex(index)
                else:
                    widget.addItem(text_value)
                    widget.setCurrentIndex(widget.count() - 1)

        except Exception as e:
            print(f"Read failed for {category_name} / {component.get('name')}: {e}")

    def handle_write(self, category_name: str, component: dict):
        """
        Called when a Write button is pressed.
        Gets the current UI value and sends it to the instrument.
        """
        widget = self.get_component_widget(category_name, component)
        command = component.get("command", "")

        if widget is None:
            print(f"Write failed: widget not found for {category_name} / {component.get('name')}")
            return

        try:
            if isinstance(widget, QLineEdit):
                value = widget.text()

            elif isinstance(widget, QComboBox):
                value = widget.currentText()

            else:
                print(f"Write failed: unsupported widget for {category_name} / {component.get('name')}")
                return

            # Replace this with your real instrument write logic
            self.instrument.write(f"{command} {value}")

        except Exception as e:
            print(f"Write failed for {category_name} / {component.get('name')}: {e}")
        
    # [+++++++++Error Handling functions++++++++++]
    
    def show_error_in_main_thread(self, msg):
        now = datetime.now()
        error_time = str(now.strftime("%Y-%m-%d--%H-%M-%S"))
        message = f"\n\n{error_time} Exception: {msg}\n\n"
        self.error_logger.append(message)
        self.errorDisplay.setText(f"<b style='color:red;'>Exception:</b>\n{msg}")
        
    def testError(self):
        raise ValueError("This is stimulated Error.")
    
    def user_filename_filter(self, text):
        print(text)
        forbidden = r'[\\/:\*\?"<>\|]'  # Windows forbidden chars
        if re.search(forbidden, text):
            self.experiment_title_note.setText(r'NOTE: A file name cannot contain \ / : * ? " < > |.')
            return False
        if len(text) > 255:
            self.experiment_title_note.setText('NOTE: Your file name is too long.')
            return False
        return True
    
    def user_pythonvariable_filter(self, text):
        if not text.isidentifier():
            return False
        if keyword.iskeyword(text):
            return False
        return True
    
    def check_instrument_connection(self):
        disconnected_instr = {}
        connected_instr = {}
        for device_model, instrument in self.instruments.items():
            if instrument.connected:
                connected_instr[device_model] = instrument
            else:
                disconnected_instr[device_model] = instrument
        print(disconnected_instr)
        return connected_instr, disconnected_instr
     
     # [/]
     
    # [+++++++++System setup functions+++++++++]
    
    def instruments_setup(self):
        folder_path = 'C:/Users/szkop/OneDrive/Desktop/YonKu/Tools/saved_instruments'
        file_pattern = "*.py"
        
        file_paths = glob.glob(f"{folder_path}/{file_pattern}")
        
        for file_path in file_paths:
            with open(file_path, 'r') as f:
                # getting the instrument info
                content = f.readline()
                content = content.strip()
                content = content.strip("#")
                
                data_list = eval(content)
                
                device_key = "Device_" + str(self.device_count)
                self.devices[device_key] = data_list
                
                # actually instantiating each instrument
                match data_list['interface']:
                    case 'serial': 
                        self.instrument_wid[device_key] = sidu.SerialInstDeviceUi(data_list)
                        self.serial_instantiate(data_list, device_key)
                    case 'gpib': 
                        self.instrument_wid[device_key] = gidu.GPIBInstDeviceUi(data_list)
                        self.gpib_instantiate(data_list, device_key)
                    case 'ethernet':
                        self.instrument_wid[device_key] = eidu.EthernetInstDeviceUi(data_list)
                        self.ethernet_instantiate(data_list, device_key)
                    case 'usb6525':
                        self.instrument_wid[device_key] = uidu.usb6525InstDeviceUi(data_list)
                        self.usb_6525_instantiate(data_list, device_key)
                    case _: self.instrument_wid[device_key] = sidu.SerialInstDeviceUi(data_list)
                    
                print(data_list)
                
                self.device_count += 1
        
        print(self.devices)   
        print("instrument setup done")

    def dataset_setup(self):
        
        self.datasets = {}
        self.datasets['primary'] = Dataset.Dataset() 
        
    def add_windows(self):
    
        for device_key, data_list in self.devices.items():
            model_name = data_list["model"]
            device_name = data_list["name"]
            
            # 1. Dynamically import the widget module
            module_path = f"GUI.instrument_control_widgets.{model_name}_widget"
            widget_module = importlib.import_module(module_path)
            
            # 2. Create the QAction
            action = QAction(f"action_{device_name}", self)
            action.setText(device_name)
            action.setCheckable(True)
            self.menuView.addAction(action)
            
            # 3. Create the widget instance
            widget_class = getattr(widget_module, f"{device_name}_widget")
            widget_instance = widget_class()
            
            # 4. Create the subwindow
            subwindow = NewQMdiSubWindow.NewQMdiSubWindow(action)
            subwindow.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
            subwindow.setWidget(widget_instance)
            subwindow.setWindowTitle(device_name)
            subwindow.resize(100, 100)
            self.mdi.addSubWindow(subwindow)
            subwindow.move(0, 0)
            subwindow.show()
            
            # 5. Store references as attributes (like exec did)
            setattr(self, f"action_{device_name}", action)
            setattr(self, f"{device_name}Wid", widget_instance)
            setattr(self, f"{device_name}Sub", subwindow)
            
            def make_view_func(subwindow=subwindow, action=action):
                def view_func():
                    if action.isChecked():
                        subwindow.show()
                    else:
                        subwindow.hide()
                return view_func

            # 7. Bind the view function dynamically
            setattr(self, f"{device_name}Sub_view", make_view_func())
    
            print(f"self.{data_list['name']}Sub")
        
        self.chA_line_sub = chs.chABigLineUi()
        # self.chA_line_sub.move(100,100)
        self.chA_line_sub.hide()
        
        self.chB_line_sub = chs.chBBigLineUi()
        # self.chB_line_sub.move(100,100)
        self.chB_line_sub.hide()
        
        self.chC_line_sub = chs.chCBigLineUi()
        # self.chC_line_sub.move(100,100)
        self.chC_line_sub.hide()
        
        self.chD_line_sub = chs.chDBigLineUi()
        # self.chD_line_sub.move(100,100)
        self.chD_line_sub.hide()
        
        # device list sub
        self.deviceListSub = dlu.DeviceListUi(self.mdi)
    
        self.deviceListSub.hide()
        
        self.esu_window = QMainWindow()
        self.experimentSettingWid = esu.ExperimentSettingUi()
        self.esu_window.setCentralWidget(self.experimentSettingWid)
        self.esu_window.setWindowTitle("Plot Setting")
        self.esu_window.resize(570, 300)
        self.esu_window.hide()
        
        print("windows setup done")
        
        for device_key, list in self.instrument_wid.items():
            self.deviceListSub.widget.tabWidget.addTab(list, device_key)
        
        QTimer.singleShot(0, self._store_initial_sizes)  
    
    def _store_initial_sizes(self):
        self._initial_mdi_size = self.mdi.size()
        for sub in self.mdi.subWindowList():
            self._initial_sub_sizes[sub] = sub.size()
    
    # will be executed automatically
    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        if not self._initial_mdi_size:
            return

        # Current size of mdiArea
        new_size = self.mdi.size()
        print(new_size)
        wid_width = int(new_size.width()/2)
        wid_height = int(new_size.height()/2)


        self.gasValveSub.resize(wid_width, wid_height)
        self.lockInAmplifier1Sub.resize(new_size.width(), new_size.height())
        self.lockInAmplifier2Sub.resize(new_size.width(), new_size.height())
        self.magnetPowerSupplySub.resize(new_size.width(), new_size.height())
        self.temperatureControllerSub.resize(wid_width,new_size.height())
        self.pressureGaugeSub.resize(wid_width,wid_height)
        
        self.gasValveSub.move(wid_width, 0)
        self.temperatureControllerSub.move(0, 0)
        self.pressureGaugeSub.move(wid_width,wid_height)

        self.lockInAmplifier1Sub.hide()
        self.lockInAmplifier2Sub.hide()
        self.magnetPowerSupplySub.hide()

    def connect_instrument_windows(self):

        for device_key, data_list in self.devices.items():
            device_name = data_list['name']
            device_Wid = getattr(self, f'{device_name}Wid')
            if self.instruments[data_list['model']].connected:
                device_Wid.setEnabled(True)
                initial_function = getattr(self, f'{device_name}_initial_function')
                initial_function()
            else:
                device_Wid.setEnabled(False)
        
        
        # [/]

    
    # [++++++++++Instrument inital function++++++++++++]
    
    
    def pressureGauge_initial_function(self):
        pass
        
    def magnetPowerSupply_initial_function(self):
        self.set_switch_heater_status()
    
    def temperatureController_initial_function(self):
        pass
    
    def lockInAmplifier2_initial_function(self):
        pass
    
    def lockInAmplifier1_initial_function(self):
        pass
    
    def gasValve_initial_function(self):
        if self.gasValve.initial_state[0]:
            self.gasValveWid.pumpPushButton.setChecked(True)
        if self.gasValve.initial_state[1]:
            self.gasValveWid.ivcPushButton.setChecked(True)
        if self.gasValve.initial_state[2]:
            self.gasValveWid.hePushButton.setChecked(True)
            # [/]

    def test_instrument_initial_function(self):
        pass
      
    # [+++++++++(Thread) experiment functions++++++++]
    def check_experiment_condition(self):
        # check error for filename
        experiment_title = self.experimentNameLineEdit.text()
        if self.user_filename_filter(experiment_title):
            pass
        else:  
            return None
        # check instrument connection
        self.connected_instuments, self.disconnected_instuments = self.check_instrument_connection()
        if not self.disconnected_instuments:
            self.start_experiment_thread()
        else:
            print("Some devices are disconnected")
            self.disDevWid = ddu.disconnected_devices_widget(self.disconnected_instuments)
            self.disDevWid.show()
            self.disDevWid.yesButton.clicked.connect(self.start_experiment_thread)
            self.disDevWid.yesButton.clicked.connect(self.disDevWid.close)
            self.disDevWid.cancelButton.clicked.connect(self.disDevWid.close)
            
    def start_experiment_thread(self):
        self.valid_period_check()
        try:
            if self.MeasureFreqLineEdit.text() == "":
                self.experiment_period = 1000
            else:
                self.experiment_period = int(self.MeasureFreqLineEdit.text()) * 1000
           
            # self.plot_worker for data acquisition
            self.plot_worker = PlotWorker(self.connected_instuments, self.plot_widgets, self.datasets['primary'].set, self.experiment_period, 
                                        self.pausePushButton, self.experimentNameLineEdit,
                                        self.lockInAmplifier1Wid.xLineEdit, self.lockInAmplifier1Wid.yLineEdit, self.lockInAmplifier1Wid.rLineEdit, self.lockInAmplifier1Wid.thetaLineEdit, 
                                        self.lockInAmplifier2Wid.xLineEdit, self.lockInAmplifier2Wid.yLineEdit, self.lockInAmplifier2Wid.rLineEdit, self.lockInAmplifier2Wid.thetaLineEdit, 
                                        self.temperatureControllerWid.chALineEdit, self.temperatureControllerWid.chBLineEdit, self.temperatureControllerWid.chCLineEdit, self.temperatureControllerWid.chDLineEdit,
                                        self.chA_line_sub.widget.chALineEdit, self.chB_line_sub.widget.chBLineEdit, 
                                        self.chC_line_sub.widget.chCLineEdit, self.chD_line_sub.widget.chDLineEdit, self.temperatureControllerWid.unitSwitchButton,
                                        self.magnetPowerSupplyWid.fieldZLineEdit,
                                        self.magnetPowerSupplyWid.currentLineEdit, self.experimentSettingWid)
            
            self.plot_worker_thread = QThread()
            self.plot_worker.moveToThread(self.plot_worker_thread)
            
            
            self.plot_worker_thread.started.connect(self.plot_worker.start_experiment)
            self.plot_worker.finished.connect(self.plot_thread_finished)
            self.plot_worker_thread.finished.connect(self.plot_worker.deleteLater)
            self.plot_worker_thread.finished.connect(self.plot_worker_thread.deleteLater)
            
            self.plot_worker_thread.start()
            
            self.plot_worker.update.connect(self.update_plot)
        
        except ValueError:
            self.experimentWid.MeasureFreqLineEdit.setText("You can only put integers here.")
        
        except Exception:
            self.errorDisplay.setText("The X and Y array sizes are different. However, you can disregard this error as long as the traces are updating real-time.")
            
    def pause_resume_experiment_thread(self):
        self.plot_worker.pause_resume_experiment()
        # self.plot_update_worker.pause_resume_experiment()
    
    def end_experiment_worker(self):
        self.plot_worker.end_experiment()
        # self.plot_update_worker.end_experiment()
        
    def plot_thread_finished(self):
        print("plot thread_finished")
        self.datasets['primary'].clear()
        self.plot_worker_thread.quit()
        self.plot_worker_thread.wait()
    
    def plot_update_thread_finished(self):
        print("plot update_thread_finished")
        self.datasets['primary'].clear()
        self.plot_update_worker_thread.quit()
        self.plot_update_worker_thread.wait()
        
    def update_plot(self):
        for index, plt_wid in self.plot_widgets.items():
            if isinstance(plt_wid, PlotUi.plotWidget):
                plt_wid.plot_data()
        
     # [/]


    # [+++++++++experiment UI functions+++++++++]
    
    def valid_period_check(self):
        try:
            if not self.MeasureFreqLineEdit.text() == "":
                self.period = int(self.MeasureFreqLineEdit.text())
            self.experiment_ongoing()
            self.pausePushButton.toggled.connect(self.experiment_paused)
            self.endAndSavePushButton.clicked.connect(self.experiment_finished)
        
        except ValueError:
            print("The experiment period is invalid")
        
    def experiment_ongoing(self):
        self.startPushButton.setText("Ongoing")
        self.startPushButton.setStyleSheet(
                "background-color: green; color: white"
            )
        self.startPushButton.setEnabled(False)
        self.pausePushButton.setEnabled(True)
        self.endAndSavePushButton.setEnabled(True)
        
    def experiment_paused(self):
        if self.pausePushButton.isChecked():
            self.pausePushButton.setText("Resume")
            self.startPushButton.setText("Paused")
            self.startPushButton.setStyleSheet(
                    "background-color: red; color: white"
                )
        else:
            self.pausePushButton.setText("Pause")
            self.startPushButton.setText("Ongoing")
            self.startPushButton.setStyleSheet(
                    "background-color: green; color: white"
                )
            
    def experiment_finished(self):
        print('experiment finished')
        
        self.pausePushButton.setText("Pause")
        self.pausePushButton.setChecked(False)
        self.pausePushButton.setEnabled(False)
        
        self.startPushButton.setText("Start")
        self.startPushButton.setStyleSheet(
                "background-color: white; color: black"
            )
        self.startPushButton.setEnabled(True)
        
        self.endAndSavePushButton.setEnabled(False)
             # [/]
    
    
    # [+++++++++Instrument UI Interface functions+++++++++++]
    
    # [...........Instrument Threads...........]
    
    def pressure_function(self):
        if self.pressureGaugeWid.startDisplay.isChecked():
            self.start_reading_pressure()
        else:
            self.pressure_worker_thread.exit()
    
    def pressureGauge_thread(self):
        print("pressure reading start")
        
        self.pressure_worker = PressureWorker(self.pressureGauge, 2000, self.pressureGaugeWid.stopDisplay, self.pressureGaugeWid.pressureGaugeLineEdit)
        self.pressure_worker_thread = QThread()
        self.pressure_worker.moveToThread(self.pressure_worker_thread)
        
        self.pressure_worker_thread.started.connect(self.pressure_worker.start_reading)
        self.pressure_worker.finished.connect(self.pressure_worker_thread.quit)
        self.pressure_worker_thread.finished.connect(self.pressure_worker.deleteLater)
        self.pressure_worker_thread.finished.connect(self.pressure_worker_thread.deleteLater)
        
        self.pressure_worker_thread.start()
        
    def magnetPowerSupply_thread(self):
        print("magnet reading start")
        
        self.magnet_worker = MagnetPowerSupplyWorker(self.magnetPowerSupply, 1000, self.magnetPowerSupplyWid.stopDisplay,
                                                     self.magnetPowerSupplyWid.temperatureLineEdit,
                                                     self.magnetPowerSupplyWid.currentLineEdit,
                                                     self.magnetPowerSupplyWid.fieldZLineEdit)
        self.magnet_worker_thread = QThread()
        self.magnet_worker.moveToThread(self.magnet_worker_thread)
        
        self.magnet_worker_thread.started.connect(self.magnet_worker.start_reading)
        self.magnet_worker.finished.connect(self.magnet_worker_thread.quit)
        self.magnet_worker_thread.finished.connect(self.magnet_worker.deleteLater)
        self.magnet_worker_thread.finished.connect(self.magnet_worker_thread.deleteLater)
        
        self.magnet_worker_thread.start()
        
    # [/]
    
    # [...........lock in amplifier...........]
    
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
        value = self.lockInAmplifier1Wid.phaseLineEdit.text()
        try:
            value = float(value)
            self.lockInAmplifier1.set_phase(value)
            
        except:
            self.lockInAmplifier1Wid.phaseLineEdit.setText("Type a valid input")

    def rs_set(self):
        value = self.lockInAmplifier1Wid.rsComboBox.currentText()
        
        if value == "Internal":
            self.lockInAmplifier1.set_trigsource(1)
            self.lockInAmplifier1Wid.rfLineEdit.setEnabled(True)
        else:
            self.lockInAmplifier1.set_trigsource(0)
            self.lockInAmplifier1Wid.rfLineEdit.setEnabled(False)
            
    def rf_set(self):
        value = self.lockInAmplifier1Wid.rfLineEdit.text()
        try:
            value = float(value)
            
            if value > 200:
                self.lockInAmplifier1Wid.syncFilComboBox.setEnabled(False)
            else:
                self.lockInAmplifier1Wid.syncFilComboBox.setEnabled(True)
            self.lockInAmplifier1.set_freq(value)
            
        except:
            self.lockInAmplifier1Wid.rfLineEdit.setText("Disabled / Invalid input")
    
    def dh_set(self):
        value = self.lockInAmplifier1Wid.dhLineEdit.text()
        try:
            value = float(value)
            if value >= 1 and value <= 19999:
                self.lockInAmplifier1.set_harm(value)
            else:
                self.lockInAmplifier1Wid.dhLineEdit.setText("Invalid input")
        except:
            self.lockInAmplifier1Wid.dhLineEdit.setText("Invalid input")
    
    def amp_set(self):
        value = self.lockInAmplifier1Wid.ampLineEdit.text()
        try:
            value = float(value)
            if value >= 0.004 and value <= 5:
                self.lockInAmplifier1.set_ampl(value)
            else:
                self.lockInAmplifier1Wid.ampLineEdit.setText("Invalid input")
        except:
            self.lockInAmplifier1Wid.ampLineEdit.setText("Invalid input")
            
    # GAIN AND TIME CONSTANT
    def sens_set(self):
        value = self.lockInAmplifier1Wid.sensComboBox.currentText()
        
        try: 
            self.lockInAmplifier1.set_sens(self.lockInAmplifier1.sensset[value])
        except KeyError:
            print("can't find the key")
            
    def reserv_set(self):
        value = self.lockInAmplifier1Wid.reservComboBox.currentText()
        
        match value:
            case "High Reserve":
                self.lockInAmplifier1.set_reserve(0)
            case "Normal":
                self.lockInAmplifier1.set_reserve(1)
            case "Low Noise":
                self.lockInAmplifier1.set_reserve(2)
            case _:
                pass
                
    def timeCnst_set(self):
        value = self.lockInAmplifier1Wid.timeCnstComboBox.currentText()
        
        try: 
            self.lockInAmplifier1.set_tau(self.lockInAmplifier1.tauset[value])
        except KeyError:
            print("can't find the key")          
        
    def lpFil_set(self):
        value = self.lockInAmplifier1Wid.lpFilComboBox.currentText()
        
        match value:
            case "6":
                self.lockInAmplifier1.set_slope(0)
            case "12":
                self.lockInAmplifier1.set_slope(1)
            case "18":
                self.lockInAmplifier1.set_slope(2)
            case "24":
                self.lockInAmplifier1.set_slope(3)
            case _:
                pass
    
    def syncFil_set(self):
        value = self.lockInAmplifier1Wid.syncFilComboBox.currentText()
        
        match value:
            case "Off":
                self.lockInAmplifier1.set_sync(0)
            case "On":
                self.lockInAmplifier1.set_sync(1)
            case _:
                pass
    
    # INPUT FILTER
    def inpConf_set(self):
        value = self.lockInAmplifier1Wid.inpConfComboBox.currentText()
        
        match value:
            case "A":
                self.lockInAmplifier1.set_input(0)
            case "B":
                self.lockInAmplifier1.set_input(1)
            case "I (1 M Ohms)":
                self.lockInAmplifier1.set_input(2)
            case "I (100 M Ohms)":
                self.lockInAmplifier1.set_input(3)
            case _:
                pass
    
    def inputShi_set(self):
        value = self.lockInAmplifier1Wid.inputShiComboBox.currentText()
        
        match value:
            case "Float":
                self.lockInAmplifier1.set_ground(0)
            case "Ground":
                self.lockInAmplifier1.set_ground(1)
            case _:
                pass
    
    def inputCoup_set(self):
        value = self.lockInAmplifier1Wid.inputCoupComboBox.currentText()
        
        match value:
            case "AC":
                self.lockInAmplifier1.set_couple(0)
            case "DC":
                self.lockInAmplifier1.set_couple(1)
            case _:
                pass
    
    def inputLnFil_set(self):
        value = self.lockInAmplifier1Wid.inputLnFilComboBox.currentText()
        
        match value:
            case "Out / No Filters":
                self.lockInAmplifier1.set_filter(0)
            case "Line Notch":
                self.lockInAmplifier1.set_filter(1)
            case "2 x Line Notch":
                self.lockInAmplifier1.set_filter(2)
            case "Both Notch Filters":
                self.lockInAmplifier1.set_filter(3)
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
        value = str(self.lockInAmplifier1.get_phase())
        self.lockInAmplifier1Wid.phaseLineEdit.setText(value)
        
    def rs_qry(self):
        value = str(self.lockInAmplifier1.get_trigsource())
        print(value)
        match value:
            case "0\n":
                print("0")
                self.lockInAmplifier1Wid.rsComboBox.setCurrentText("External")
            case "1\n":
                print("1")
                self.lockInAmplifier1Wid.rsComboBox.setCurrentText("Internal")   
            case _:
                pass
    
    def rf_qry(self):
        value = str(self.lockInAmplifier1.get_freq())
        self.lockInAmplifier1Wid.rfLineEdit.setText(value)
        
    def dh_qry(self):
        value = str(self.lockInAmplifier1.get_harm())
        self.lockInAmplifier1Wid.dhLineEdit.setText(value)
        
    def amp_qry(self):
        value = str(self.lockInAmplifier1.get_ampl())
        self.lockInAmplifier1Wid.ampLineEdit.setText(value)
    
    # GAIN AND TIME CONSTANT
    def sens_qry(self):
        index = str(self.lockInAmplifier1.get_sens())
        print(index)
        
        value = list(self.lockInAmplifier1.sensset.keys())[int(index)]
        
        self.lockInAmplifier1Wid.sensComboBox.setCurrentText(value)
        
    def reserv_qry(self):
        value = str(self.lockInAmplifier1.get_reserve())
        print(value)
        match value:
            case "0\n":
                print("0")
                self.lockInAmplifier1Wid.rsComboBox.setCurrentText("High Reserve")
            case "1\n":
                print("1")
                self.lockInAmplifier1Wid.rsComboBox.setCurrentText("Normal") 
            case "2\n":
                print("2")
                self.lockInAmplifier1Wid.rsComboBox.setCurrentText("Low Noise")   
            case _:
                pass
            
    def timeCnst_qry(self):
        index = str(self.lockInAmplifier1.get_tau())
        print(index)
        
        value = list(self.lockInAmplifier1.tauset.keys())[int(index)]
        
        self.lockInAmplifier1Wid.timeCnstComboBox.setCurrentText(value)
        
    def lpFil_qry(self):
        value = str(self.lockInAmplifier1.get_slope())
        print(value)
        match value:
            case "0\n":
                print("0")
                self.lockInAmplifier1Wid.rsComboBox.setCurrentText("6")
            case "1\n":
                print("1")
                self.lockInAmplifier1Wid.rsComboBox.setCurrentText("12") 
            case "2\n":
                print("2")
                self.lockInAmplifier1Wid.rsComboBox.setCurrentText("18")
            case "3\n":
                print("3")
                self.lockInAmplifier1Wid.rsComboBox.setCurrentText("24")      
            case _:
                pass
            
    def syncFil_qry(self):
        value = str(self.lockInAmplifier1.get_sync())
        print(value)
        match value:
            case "0\n":
                print("0")
                self.lockInAmplifier1Wid.rsComboBox.setCurrentText("Off")
            case "1\n":
                print("1")
                self.lockInAmplifier1Wid.rsComboBox.setCurrentText("On")   
            case _:
                pass
    
    # INPUT FILTER
    def inpConf_qry(self):
        value = str(self.lockInAmplifier1.get_input())
        match value:
            case "0\n":
                print("0")
                self.lockInAmplifier1Wid.rsComboBox.setCurrentText("A")
            case "1\n":
                print("1")
                self.lockInAmplifier1Wid.rsComboBox.setCurrentText("B") 
            case "2\n":
                print("2")
                self.lockInAmplifier1Wid.rsComboBox.setCurrentText("I (1 M Ohms)")
            case "3\n":
                print("3")
                self.lockInAmplifier1Wid.rsComboBox.setCurrentText("I (100 M Ohms)")      
            case _:
                pass
            
    def inputShi_qry(self):
        value = str(self.lockInAmplifier1.get_ground())
        print(value)
        match value:
            case "0\n":
                print("0")
                self.lockInAmplifier1Wid.rsComboBox.setCurrentText("Float")
            case "1\n":
                print("1")
                self.lockInAmplifier1Wid.rsComboBox.setCurrentText("Ground")    
            case _:
                pass
            
    def inputCoup_qry(self):
        value = str(self.lockInAmplifier1.get_couple())
        print(value)
        match value:
            case "0\n":
                print("0")
                self.lockInAmplifier1Wid.rsComboBox.setCurrentText("AC")
            case "1\n":
                print("1")
                self.lockInAmplifier1Wid.rsComboBox.setCurrentText("DC")    
            case _:
                pass
            
    def inputLnFil_qry(self): 
        value = str(self.lockInAmplifier1.get_filter())
        match value: 
            case "0\n":
                print("0")
                self.lockInAmplifier1Wid.rsComboBox.setCurrentText("Out / No Filters")
            case "1\n":
                print("1")
                self.lockInAmplifier1Wid.rsComboBox.setCurrentText("Line Notch") 
            case "2\n":
                print("2")
                self.lockInAmplifier1Wid.rsComboBox.setCurrentText("2 x Line Notch")
            case "3\n":
                print("3")
                self.lockInAmplifier1Wid.rsComboBox.setCurrentText("Both Notch Filters")      
            case _:
                pass
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
        value = self.lockInAmplifier2Wid.phaseLineEdit.text()
        try:
            value = float(value)
            self.lockInAmplifier2.set_phase(value)
            
        except:
            self.lockInAmplifier2Wid.phaseLineEdit.setText("Type a valid input")

    def rs_set2(self):
        value = self.lockInAmplifier2Wid.rsComboBox.currentText()
        
        if value == "Internal":
            self.lockInAmplifier2.set_trigsource(1)
            self.lockInAmplifier2Wid.rfLineEdit.setEnabled(True)
        else:
            self.lockInAmplifier2.set_trigsource(0)
            self.lockInAmplifier2Wid.rfLineEdit.setEnabled(False)
            
    def rf_set2(self):
        value = self.lockInAmplifier2Wid.rfLineEdit.text()
        try:
            value = float(value)
            
            if value > 200:
                self.lockInAmplifier2Wid.syncFilComboBox.setEnabled(False)
            else:
                self.lockInAmplifier2Wid.syncFilComboBox.setEnabled(True)
            self.lockInAmplifier2.set_freq(value)
            
        except:
            self.lockInAmplifier2Wid.rfLineEdit.setText("Disabled / Invalid input")
    
    def dh_set2(self):
        value = self.lockInAmplifier2Wid.dhLineEdit.text()
        try:
            value = float(value)
            if value >= 1 and value <= 19999:
                self.lockInAmplifier2.set_harm(value)
            else:
                self.lockInAmplifier2Wid.dhLineEdit.setText("Invalid input")
        except:
            self.lockInAmplifier2Wid.dhLineEdit.setText("Invalid input")
            
    # GAIN AND TIME CONSTANT
    def sens_set2(self):
        value = self.lockInAmplifier2Wid.sensComboBox.currentText()
        
        try: 
            self.lockInAmplifier2.set_sens(self.lockInAmplifier2.sensset[value])
        except KeyError:
            print("can't find the key")
            
    def reserv_set2(self):
        value = self.lockInAmplifier2Wid.reservComboBox.currentText()
        
        match value:
            case "High Reserve":
                self.lockInAmplifier2.set_reserve(0)
            case "Normal":
                self.lockInAmplifier2.set_reserve(1)
            case "Low Noise":
                self.lockInAmplifier2.set_reserve(2)
            case _:
                pass
                
    def timeCnst_set2(self):
        value = self.lockInAmplifier2Wid.timeCnstComboBox.currentText()
        
        try: 
            self.lockInAmplifier2.set_tau(self.lockInAmplifier2.tauset[value])
        except KeyError:
            print("can't find the key")          
        
    def lpFil_set2(self):
        value = self.lockInAmplifier2Wid.lpFilComboBox.currentText()
        
        match value:
            case "6":
                self.lockInAmplifier2.set_slope(0)
            case "12":
                self.lockInAmplifier2.set_slope(1)
            case "18":
                self.lockInAmplifier2.set_slope(2)
            case "24":
                self.lockInAmplifier2.set_slope(3)
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
        value = str(self.lockInAmplifier2.get_phase())
        self.lockInAmplifier2Wid.phaseLineEdit.setText(value)
        
    def rs_qry2(self):
        value = str(self.lockInAmplifier2.get_trigsource())
        print(value)
        match value:
            case "0\n":
                print("0")
                self.lockInAmplifier2Wid.rsComboBox.setCurrentText("External")
            case "1\n":
                print("1")
                self.lockInAmplifier2Wid.rsComboBox.setCurrentText("Internal")   
            case _:
                pass
    
    def rf_qry2(self):
        value = str(self.lockInAmplifier2.get_freq())
        self.lockInAmplifier2Wid.rfLineEdit.setText(value)
        
    def dh_qry2(self):
        value = str(self.lockInAmplifier2.get_harm())
        self.lockInAmplifier2Wid.dhLineEdit.setText(value)
        
    # GAIN AND TIME CONSTANT
    def sens_qry2(self):
        index = str(self.lockInAmplifier2.get_sens())
        print(index)
        
        value = list(self.lockInAmplifier2.sensset.keys())[int(index)]
        
        self.lockInAmplifier2Wid.sensComboBox.setCurrentText(value)
        
    def reserv_qry2(self):
        value = str(self.lockInAmplifier2.get_reserve())
        print(value)
        match value:
            case "0\n":
                print("0")
                self.lockInAmplifier2Wid.rsComboBox.setCurrentText("High Reserve")
            case "1\n":
                print("1")
                self.lockInAmplifier2Wid.rsComboBox.setCurrentText("Normal") 
            case "2\n":
                print("2")
                self.lockInAmplifier2Wid.rsComboBox.setCurrentText("Low Noise")   
            case _:
                pass
            
    def timeCnst_qry2(self):
        index = str(self.lockInAmplifier2.get_tau())
        print(index)
        
        value = list(self.lockInAmplifier2.tauset.keys())[int(index)]
        
        self.lockInAmplifier2Wid.timeCnstComboBox.setCurrentText(value)
        
    def lpFil_qry2(self):
        value = str(self.lockInAmplifier2.get_slope())
        print(value)
        match value:
            case "0\n":
                print("0")
                self.lockInAmplifier2Wid.rsComboBox.setCurrentText("6")
            case "1\n":
                print("1")
                self.lockInAmplifier2Wid.rsComboBox.setCurrentText("12") 
            case "2\n":
                print("2")
                self.lockInAmplifier2Wid.rsComboBox.setCurrentText("18")
            case "3\n":
                print("3")
                self.lockInAmplifier2Wid.rsComboBox.setCurrentText("24")      
            case _:
                pass
            

    # [/]
# [/]
   
    # [...........temperature controller...........]
        
    def expand_chA_line(self):
        self.chA_line_sub.show()
        
    def expand_chB_line(self):
        self.chB_line_sub.show()
    
    def expand_chC_line(self):
        self.chC_line_sub.show()
    
    def expand_chD_line(self):
        self.chD_line_sub.show()
      # [/]
   
    # [...........gas valve...........]
    
    def pump_change(self):
        if self.gasValveWid.pumpPushButton.isChecked():
            self.gasValve.turn_on_SV1()
        else:
            self.gasValve.turn_off_SV1()
    
    def ivc_change(self):
        if self.gasValveWid.ivcPushButton.isChecked():
            self.gasValve.turn_on_SV2()
        else:
            self.gasValve.turn_off_SV2()
    
    def he_change(self):
        if self.gasValveWid.hePushButton.isChecked():
            self.gasValve.turn_on_SV3()
        else:
            self.gasValve.turn_off_SV3()  
    
    def gas_all_off(self):
        self.gasValve.turn_off_all()      
    
    def gas_all_on(self):
        self.gasValve.turn_on_all()
         # [/]

    # [...........magnet supply...........]
    
    def switch_heater_power(self):
        if self.magnetPowerSupplyWid.switchHeaterZbutton.isChecked():
            self.magnetPowerSupply.set_switch_status('Z','ON')
        else:
            self.magnetPowerSupply.set_switch_status('Z','OFF')
    
    def set_switch_heater_status(self):

        switch_heater_status = self.magnetPowerSupply.read_all_switch_status()
        
        x_status = switch_heater_status['x'].split(':')[-1]
        y_status = switch_heater_status['y'].split(':')[-1]
        z_status = switch_heater_status['z'].split(':')[-1]
        
        print(x_status, y_status, z_status)
        
        if z_status == 'ON':
            self.magnetPowerSupplyWid.on_state(self.magnetPowerSupplyWid.switchHeaterZbutton)
        else:
            self.magnetPowerSupplyWid.off_state(self.magnetPowerSupplyWid.switchHeaterZbutton)
        
        self.magnetPowerSupplyWid.switchHeaterZLineEdit.setText('')
        
    def set_target_field(self):
        value = self.magnetPowerSupplyWid.targetFieldSpinBox.value()
        response = self.magnetPowerSupply.set_target_field('Z', str(value))
        print(response)
    
    def read_target_field(self):
        value = self.magnetPowerSupply.read_target_field('Z')
        print(value)
        self.magnetPowerSupplyWid.targetFieldSpinBox.setValue(float(value))
        
    def set_field_rate(self):
        value = self.magnetPowerSupplyWid.fieldRatingSpinBox.value()
        response = self.magnetPowerSupply.set_field_rate('Z', str(value))
        print(response)
    
    def read_field_rate(self):
        value = self.magnetPowerSupply.read_field_rate('Z')
        print(value)
        self.magnetPowerSupplyWid.fieldRatingSpinBox.setValue(float(value))
    
    # [/]
         # [/]
    
    
    # [+++++++++Plot UI Interface functions]
    
    # [...........new plots...........]
    
    def new_plot_setting(self):
        self.nps_window = QMainWindow()
        self.newPlotSettingWid = nps.create_plot_setting_ui()
        # self.Wid = QWidget()
        # uic.loadUi("GUI/create_plot_setting.ui", self.Wid)
        self.nps_window.setCentralWidget(self.newPlotSettingWid)
        self.nps_window.setWindowTitle("Plot Setting")
        self.nps_window.resize(440, 320)
        self.nps_window.show()
        
        self.newPlotSettingWid.CreatePlotPushButton.clicked.connect(self.create_plot)
        
    def create_plot(self):
        self.newPlotSettingWid.update_values()
        self.plot_setting = [self.newPlotSettingWid.xAxisUnit, self.newPlotSettingWid.yAxisUnit, self.newPlotSettingWid.xAxisHiLim, 
                      self.newPlotSettingWid.xAxisLoLim, self.newPlotSettingWid.yAxisHiLim, self.newPlotSettingWid.yAxisLoLim, 
                      self.newPlotSettingWid.tickVal, self.newPlotSettingWid.gridLine, self.newPlotSettingWid.symbol, self.experimentSettingWid]
        print(self.plot_setting)
        self.nps_window.close()
        self.new_plot_window()

    def new_plot_window(self):
        self.plot_widgets[self.plot_widget_count] = PlotUi.plotWidget(self.plot_setting, self.datasets['primary'].set, self.experimentSettingWid.experiment_parameters)
        
        self.plot_sub = QMdiSubWindow()
        self.plot_sub.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint) # disable maximize button
        self.plot_sub.setWidget(self.plot_widgets[self.plot_widget_count])
        self.plot_sub.setWindowTitle("Plot")
        self.plot_sub.resize(700,700)
        self.mdi_plot.addSubWindow(self.plot_sub)
        self.plot_sub.move(0,0)
        self.plot_sub.show()
        
        # self.check_newPlotB_clicked(self.plot_count)
        
        # print(self.plot_widgets)
        
        self.plot_widget_count += 1 
        
        
        
        # [/]
    
    # [...........old plots...........]
    
    def open_plot_setting(self):
        self.ops_window = QMainWindow()
        self.openPlotSettingWid = ops.create_plot_setting_ui()
        # self.Wid = QWidget()
        # uic.loadUi("GUI/create_plot_setting.ui", self.Wid)
        self.ops_window.setCentralWidget(self.openPlotSettingWid)
        self.ops_window.setWindowTitle("Plot Setting")
        self.ops_window.resize(440, 370)
        self.ops_window.show()
        
        self.openPlotSettingWid.CreatePlotPushButton.clicked.connect(self.create_old_plot)
    
    def create_old_plot(self):
        try:
            self.openPlotSettingWid.update_values() #update the open plot setting values
            
            # Check if the selected dataset has the desired data type
            self.xAxis_exists = False
            self.yAxis_exists = False
            
            try:
                param_file = open(self.openPlotSettingWid.experimentParam)    
                param_file_content = param_file.readlines()
                connected_instruments = eval(param_file_content[59].replace("\n",""))
                print(connected_instruments)
            except SyntaxError: # in case we are opening databases from before the latest version
                print(e)
                connected_instruments = ['Lakeshore_336', 'Oxford_MercuryiPS', 'SRS_830', 'SRS_830_2']
            except FileNotFoundError as e:
                print(e)
                print("Error detected at the nested level")
                connected_instruments = ['Lakeshore_336', 'Oxford_MercuryiPS', 'SRS_830', 'SRS_830_2']
            except UnboundLocalError as e:
                print(e)
                connected_instruments = ['Lakeshore_336', 'Oxford_MercuryiPS', 'SRS_830', 'SRS_830_2']
                
            for instrument in connected_instruments:
                for data_type in list(self.instruments[instrument].data_type.keys()):
                    print(data_type)
                    if data_type == self.openPlotSettingWid.xAxisUnit:
                        self.xAxis_exists = True
                    if data_type == self.openPlotSettingWid.yAxisUnit:
                        self.yAxis_exists = True
                    print([self.xAxis_exists,self.yAxis_exists])
            
            if self.openPlotSettingWid.xAxisUnit == 'time':
                self.xAxis_exists = True
            if self.openPlotSettingWid.yAxisUnit == 'time':
                self.yAxis_exists = True
            
            if self.xAxis_exists and self.yAxis_exists:
                self.plot_setting = [self.openPlotSettingWid.xAxisUnit, self.openPlotSettingWid.yAxisUnit, self.openPlotSettingWid.xAxisHiLim, 
                            self.openPlotSettingWid.xAxisLoLim, self.openPlotSettingWid.yAxisHiLim, self.openPlotSettingWid.yAxisLoLim, 
                            self.openPlotSettingWid.tickVal, self.openPlotSettingWid.gridLine, self.openPlotSettingWid.dataset, self.openPlotSettingWid.multipleDataset,
                            self.openPlotSettingWid.experimentParam, connected_instruments]
                self.old_plot_window()
                print(self.plot_setting)
                self.ops_window.close()
            
            else:
                self.openPlotSettingWid.browseDatasetLineEdit.setText("This dataset doesn't include the chosen data types.")
            
        except FileNotFoundError as e:
            print(e)
            self.openPlotSettingWid.browseDatasetLineEdit.setText("You have to choose a database to open.")
        
    def old_plot_window(self):
        self.plot_widgets[self.plot_widget_count] = PlotUi.oldPlotWidget(self.plot_setting, self.instruments)
        self.plot_sub = QMdiSubWindow()
        self.plot_sub.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint) # disable maximize button
        self.plot_sub.setWidget(self.plot_widgets[self.plot_widget_count])
        
        if self.openPlotSettingWid.multipleDataset:
            self.plot_sub.setWindowTitle("MultiDataset Plot")
        else:
            self.plot_sub.setWindowTitle(self.openPlotSettingWid.dataset)
        self.plot_sub.resize(700,700)
        self.mdi_plot.addSubWindow(self.plot_sub)
        self.plot_sub.move(0,0)
        self.plot_sub.show()
        
        self.plot_widget_count += 1
        
     # [/]
     # [/]
    
    
    # [++++++++++Menu Bar UI Interface functions++++++++++]
        
    # [...........menu bar DEVICE...........]
    
    def serial_instrument_create(self):
        self.serial_inst_create_wid = sic.SerialInstCreateUi()
        self.serial_inst_create_sub = QMdiSubWindow()
        self.mdi.addSubWindow(self.serial_inst_create_sub)
        
        self.serial_inst_create_sub.setWidget(self.serial_inst_create_wid)
        self.serial_inst_create_sub.setWindowTitle("Add a Serial Instrument")
        self.serial_inst_create_sub.resize(570, 470)
        self.serial_inst_create_sub.move(500, 200)
        
        self.serial_inst_create_sub.show()
        
        self.serial_inst_create_wid.cancelButton.clicked.connect(self.serial_close)
        self.serial_inst_create_wid.saveButton.clicked.connect(self.serial_save_device)
        
    def serial_close(self):
        self.serial_inst_create_sub.hide()

    def serial_save_device(self):
        self.serial_inst_create_sub.hide()
        
        self.serial_inst_create_wid.update_parameters()
        
        directory_path = "C:/Users/szkop/OneDrive/Desktop/YonKu/Tools/saved_instruments"
        file_name = self.serial_inst_create_wid.data_list['model'] + '.py'
        
        full_file_path = os.path.join(directory_path, file_name)
        os.makedirs(directory_path, exist_ok=True)
        with open(full_file_path, "w") as f:
            f.write(self.serial_inst_create_wid.device_script())
            
        with open(full_file_path, 'r') as f:
            content = f.readline()
            content = content.strip()
            content = content.strip("#")
            # Process the content as needed
            # print(content)
            
            data_list = eval(content)
            
            device_key = "Device_" + str(self.device_count)
            self.devices[device_key] = data_list
            self.instrument_wid[device_key] = sidu.SerialInstDeviceUi(data_list)
            self.serial_instantiate(data_list, device_key)

                
            print(data_list)
            
            self.device_count += 1
            
        self.deviceListSub.widget.tabWidget.addTab(self.instrument_wid[device_key], device_key)
        
        self.serial_device_wid_create()

    def serial_device_wid_create(self):
        directory_path = "C:/Users/szkop/OneDrive/Desktop/YonKu/GUI/ui_files/instrument_control_uis"
        file_name = self.serial_inst_create_wid.data_list['model'] + '_ui' + '.ui'
        
        full_file_path = os.path.join(directory_path, file_name)
        os.makedirs(directory_path, exist_ok=True)
        with open(full_file_path, "w") as f:
            f.write(self.serial_inst_create_wid.device_ui_script())
        
        directory_path = "C:/Users/szkop/OneDrive/Desktop/YonKu/GUI/instrument_control_widgets"
        file_name = self.serial_inst_create_wid.data_list['model'] + '_widget' + '.py'
        
        full_file_path = os.path.join(directory_path, file_name)
        os.makedirs(directory_path, exist_ok=True)
        with open(full_file_path, "w") as f:
            f.write(self.serial_inst_create_wid.device_wid_script())
        

    def serial_instantiate(self, data_list, device_key):
        model_name = data_list["model"]
        device_name = data_list["name"]
        port = data_list['port']
        
        module_path = f"Tools.saved_instruments.{model_name}"
        try:
            instrument_module = importlib.import_module(module_path)
        except ImportError as e:
            print(f"Warning: Could not import module '{module_path}': {e}")
        
        try:
            instrument_class = getattr(instrument_module, device_name)
        except AttributeError:
            print(f"Warning: '{device_name}' not found in module '{module_path}'.")
            
        try:
            serial_instrument = instrument_class(device_name, port)
        except Exception as e:
            print(f"Error instantiating '{device_name}': {e}")
        
        setattr(self, device_name, serial_instrument)
        self.instruments[model_name] = serial_instrument
            
        if self.instruments[model_name].connected:
            self.instrument_wid[device_key].connectionLineEdit.setText("Connected")
            self.instrument_wid[device_key].instrument = serial_instrument
        else:
            self.instrument_wid[device_key].connectionLineEdit.setText("Not Connected")


    def gpib_instrument_create(self):
        self.gpib_inst_create_wid = gic.GpibInstCreateUi()
        self.gpib_inst_create_sub = QMdiSubWindow()
        self.mdi.addSubWindow(self.gpib_inst_create_sub)
        
        self.gpib_inst_create_sub.setWidget(self.gpib_inst_create_wid)
        self.gpib_inst_create_sub.setWindowTitle("Add a GPIB Instrument")
        self.gpib_inst_create_sub.resize(570, 470)
        self.gpib_inst_create_sub.move(500, 200)
        
        self.gpib_inst_create_sub.show()
        
        self.gpib_inst_create_wid.cancelButton.clicked.connect(self.gpib_close)
        self.gpib_inst_create_wid.saveButton.clicked.connect(self.gpib_save_device)
        
    def gpib_close(self):
        self.gpib_inst_create_sub.hide()
        
    def gpib_save_device(self):
        self.gpib_inst_create_sub.hide()
        
        self.gpib_inst_create_wid.update_parameters()
        
        directory_path = "C:/Users/szkop/OneDrive/Desktop/YonKu/Tools/saved_instruments"
        file_name = self.gpib_inst_create_wid.data_list['model'] + '.py'
        
        full_file_path = os.path.join(directory_path, file_name)
        os.makedirs(directory_path, exist_ok=True)
        with open(full_file_path, "w") as f:
            f.write(self.gpib_inst_create_wid.device_script())
            
        with open(full_file_path, 'r') as f:
            content = f.readline()
            content = content.strip()
            content = content.strip("#")
            # Process the content as needed
            # print(content)
            
            data_list = eval(content)
            
            device_key = "Device_" + str(self.device_count)
            self.devices[device_key] = data_list
            self.instrument_wid[device_key] = gidu.GPIBInstDeviceUi(data_list)
            self.gpib_instantiate(data_list, device_key)
                
            print(data_list)
            
            self.device_count += 1
            
        self.deviceListSub.widget.tabWidget.addTab(self.instrument_wid[device_key], device_key)
        
    def gpib_instantiate(self, data_list, device_key):
        model_name = data_list["model"]
        device_name = data_list["name"]
        address = data_list['address']
        
        module_path = f"Tools.saved_instruments.{model_name}"
        try:
            instrument_module = importlib.import_module(module_path)
        except ImportError as e:
            print(f"Warning: Could not import module '{module_path}': {e}")
        
        try:
            instrument_class = getattr(instrument_module, device_name)
        except AttributeError:
            print(f"Warning: '{device_name}' not found in module '{module_path}'.")
            
        try:
            gpib_instrument = instrument_class(device_name, address)
        except Exception as e:
            print(f"Error instantiating '{device_name}': {e}")
        
        setattr(self, device_name, gpib_instrument)
        self.instruments[model_name] = gpib_instrument
            
        if self.instruments[model_name].connected:
            self.instrument_wid[device_key].connectionLineEdit.setText("Connected")
            self.instrument_wid[device_key].instrument = gpib_instrument
        else:
            self.instrument_wid[device_key].connectionLineEdit.setText("Not Connected")
            
       
    def ethernet_instrument_create(self):
        self.ethernet_inst_create_wid = eic.EthernetInstCreateUi()
        self.ethernet_inst_create_sub = QMdiSubWindow()
        self.mdi.addSubWindow(self.ethernet_inst_create_sub)
        
        self.ethernet_inst_create_sub.setWidget(self.ethernet_inst_create_wid)
        self.ethernet_inst_create_sub.setWindowTitle("Add a GPIB Instrument")
        self.ethernet_inst_create_sub.resize(570, 470)
        self.ethernet_inst_create_sub.move(500, 200)
        
        self.ethernet_inst_create_sub.show()
        
        self.ethernet_inst_create_wid.cancelButton.clicked.connect(self.ethernet_close)
        self.ethernet_inst_create_wid.saveButton.clicked.connect(self.ethernet_save_device)
            
    def ethernet_close(self):
        self.ethernet_inst_create_sub.hide()
        
    def ethernet_save_device(self):
        self.ethernet_inst_create_sub.hide()
        
        self.ethernet_inst_create_wid.update_parameters()
        
        directory_path = "C:/Users/szkop/OneDrive/Desktop/YonKu/Tools/saved_instruments"
        file_name = self.ethernet_inst_create_wid.data_list['model'] + '.py'
        
        full_file_path = os.path.join(directory_path, file_name)
        os.makedirs(directory_path, exist_ok=True)
        with open(full_file_path, "w") as f:
            f.write(self.ethernet_inst_create_wid.device_script())
            
        with open(full_file_path, 'r') as f:
            content = f.readline()
            content = content.strip()
            content = content.strip("#")
            # Process the content as needed
            # print(content)
            
            data_list = eval(content)
            
            device_key = "Device_" + str(self.device_count)
            self.devices[device_key] = data_list
            self.instrument_wid[device_key] = eidu.EthernetnstDeviceUi(data_list)
            self.ethernet_instantiate(data_list, device_key)
                
            print(data_list)
            
            self.device_count += 1
            
        self.deviceListSub.widget.tabWidget.addTab(self.instrument_wid[device_key], device_key)
        
    def ethernet_instantiate(self, data_list, device_key):
        model_name = data_list["model"]
        device_name = data_list["name"]
        inst_IP = data_list['instIP']
        port = data_list['port']
        
        module_path = f"Tools.saved_instruments.{model_name}"
        try:
            instrument_module = importlib.import_module(module_path)
        except ImportError as e:
            print(f"Warning: Could not import module '{module_path}': {e}")
        
        try:
            instrument_class = getattr(instrument_module, device_name)
        except AttributeError:
            print(f"Warning: '{device_name}' not found in module '{module_path}'.")
            
        try:
            ethernet_instrument = instrument_class(device_name, 
                                            inst_IP, 
                                            int(port))
        except Exception as e:
            print(f"Error instantiating '{device_name}': {e}")
        
        setattr(self, device_name, ethernet_instrument)
        self.instruments[model_name] = ethernet_instrument
            
        if self.instruments[model_name].connected:
            self.instrument_wid[device_key].connectionLineEdit.setText("Connected")
            self.instrument_wid[device_key].instrument = ethernet_instrument
        else:
            self.instrument_wid[device_key].connectionLineEdit.setText("Not Connected")
  
        
    def usb_6525_instrument_create(self):
        self.usb_6525_inst_create_wid = bic.usb6525InstCreateUi()
        self.usb_6525_inst_create_sub = QMdiSubWindow()
        self.mdi.addSubWindow(self.usb_6525_inst_create_sub)
        
        self.usb_6525_inst_create_sub.setWidget(self.usb_6525_inst_create_wid)
        self.usb_6525_inst_create_sub.setWindowTitle("Add a GPIB Instrument")
        self.usb_6525_inst_create_sub.resize(570, 470)
        self.usb_6525_inst_create_sub.move(500, 200)
        
        self.usb_6525_inst_create_sub.show()
        
        self.usb_6525_inst_create_wid.cancelButton.clicked.connect(self.usb_6525_close)
        self.usb_6525_inst_create_wid.saveButton.clicked.connect(self.usb_6525_save_device)
        
    def usb_6525_close(self):
        self.usb_6525_inst_create_sub.hide()
        
    def usb_6525_save_device(self):
        self.usb_6525_inst_create_sub.hide()
        
        self.usb_6525_inst_create_wid.update_parameters()
        
        directory_path = "C:/Users/szkop/OneDrive/Desktop/YonKu/Tools/saved_instruments"
        file_name = self.usb_6525_inst_create_wid.data_list['model'] + '.py'
        
        full_file_path = os.path.join(directory_path, file_name)
        os.makedirs(directory_path, exist_ok=True)
        with open(full_file_path, "w") as f:
            f.write(self.usb_6525_inst_create_wid.device_script())
            
        with open(full_file_path, 'r') as f:
            content = f.readline()
            content = content.strip()
            content = content.strip("#")
            # Process the content as needed
            # print(content)
            
            data_list = eval(content)
            
            device_key = "Device_" + str(self.device_count)
            self.devices[device_key] = data_list
            self.instrument_wid[device_key] = uidu.usb6525InstDeviceUi(data_list)
            self.usb_6525_instantiate(data_list, device_key)
            
                
            print(data_list)
            
            self.device_count += 1
            
        self.deviceListSub.widget.tabWidget.addTab(self.instrument_wid[device_key], device_key)
        
    def usb_6525_instantiate(self, data_list, device_key):
        model_name = data_list["model"]
        device_name = data_list["name"]
        
        module_path = f"Tools.saved_instruments.{model_name}"
        try:
            instrument_module = importlib.import_module(module_path)
        except ImportError as e:
            print(f"Warning: Could not import module '{module_path}': {e}")
        
        try:
            instrument_class = getattr(instrument_module, device_name)
        except AttributeError:
            print(f"Warning: '{device_name}' not found in module '{module_path}'.")
            
        try:
            usb_instrument = instrument_class(device_name, 
                                            f'Dev{data_list['deviceNumber']}', 
                                            f'port{data_list['port']}', 
                                            f'line{data_list['range1']}:{data_list['range2']}')
        except Exception as e:
            print(f"Error instantiating '{device_name}': {e}")
        
        setattr(self, device_name, usb_instrument)
        self.instruments[model_name] = usb_instrument
            
        if self.instruments[model_name].connected:
            self.instrument_wid[device_key].connectionLineEdit.setText("Connected")
            self.instrument_wid[device_key].instrument = usb_instrument
        else:
            self.instrument_wid[device_key].connectionLineEdit.setText("Not Connected")
           
        
        

    def device_list_show(self):
        self.deviceListSub.show()
 
    # [/]

    
    # [...........menu bar EXPERIMENT...........]
    
    def experiment_setting_create(self):
        self.esu_window.show()
        self.experimentSettingWid.cancelButton.clicked.connect(self.experiment_setting_close)
    
    def experiment_setting_close(self):
        self.esu_window.hide() # [/]
     # [/]
    

    # [++++++++++closeEvent functions++++++++]
    
    def closeEvent(self, event:QCloseEvent):
        # Implement your custom logic here
        reply = QMessageBox.question(self, 'Confirmation',
                                        "Are you sure you want to quit?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # If you want to allow the close event, call accept()
            
            try:
                self.pressure_thread_finished()
            except:
                pass
            
            try:
                self.end_experiment_worker()
            except:
                pass
            
            for name, device in self.instruments.items():
                self.instruments[name].close()
            
            with open(self.error_logger.file_path, "r") as f:
                error_log = f.read()
                f.close()
                
            if error_log == self.error_logger.heading:
                os.remove(self.error_logger.file_path)
            else:
                pass
            
            event.accept()
            QApplication.instance().closeAllWindows()
        else:
            # If you want to prevent the close event, call ignore()
            event.ignore()
         # [/]
        
         # [/]
        
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    UIWindow = UI()
    app.exec()
    
    
    