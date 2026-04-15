from pathlib import Path
import sys
import re
import keyword
import os
import glob
import json
import traceback
import importlib

from PyQt5.QtWidgets import QMainWindow, QApplication, QMdiSubWindow, QMessageBox, QAction, QMdiSubWindow
from PyQt5.QtCore import QThread, QObject, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QCloseEvent
from PyQt5 import uic

from GUI import NewPlotSettingUi as nps, OpenPlotSettingUi as ops, PlotUi, ExperimentSettingUi as esu
from GUI import SerialInstCreateUi as sic, GpibInstCreateUi as gic, EthernetInstCreateUi as eic, USB6525InstCreateUi as bic, DisconnectedDevicesUi as ddu
from GUI import DeviceListUi as dlu, SerialInstDeviceUi as sidu, GpibInstDeviceUi as gidu, EthernetInstDeviceUi as eidu, USB6525InstDeviceUi as uidu
from Tools import DataLogger, Dataset, NewQMdiSubWindow, ExperimentController


from datetime import datetime

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
        self.devices = {}       # self.devices = {'device_key' : data_list }
        self.device_count = 0

        self.plot_widgets = {}
        self.plot_widget_count = 0
        
            # [/]
        
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
            action = getattr(self, f"action_{device_name}", QAction())
            subwindow = getattr(self, f"{device_name}Sub", QMdiSubWindow())
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

        
        self.showMaximized()
        self.show()  # [/]
        

    # [Functions]

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
        for device_key, instrument in self.instruments.items():
            if instrument.connected:
                connected_instr[device_key] = instrument
            else:
                disconnected_instr[device_key] = instrument
        print(disconnected_instr)
        return connected_instr, disconnected_instr
     
     # [/]
     
     
    # [+++++++++System setup functions+++++++++]
    
    def instruments_setup(self):
        folder_path = Path("C:/Users/szkop/OneDrive/Desktop/YonKu/Data/saved_devices")

        config_files = folder_path.glob("*.json")

        for file_path in config_files:
            with open(file_path, "r", encoding="utf-8") as f:
                data_list = json.load(f)

            device_key = f"Device_{self.device_count}"
            self.devices[device_key] = data_list

            try:   
                # actually instantiating each instrument
                match data_list['interface']:
                    case 'serial': 
                        self.instrument_wid[device_key] = sidu.SerialInstDeviceUi(data_list)
                        self.instantiate_device(data_list, device_key, 'serial')
                    case 'gpib': 
                        self.instrument_wid[device_key] = gidu.GPIBInstDeviceUi(data_list)
                        self.instantiate_device(data_list, device_key, 'gpib')
                    case 'ethernet':
                        self.instrument_wid[device_key] = eidu.EthernetInstDeviceUi(data_list)
                        self.instantiate_device(data_list, device_key, 'ethernet')
                    case 'usb6525':
                        self.instrument_wid[device_key] = uidu.usb6525InstDeviceUi(data_list)
                        self.instantiate_device(data_list, device_key, 'usb6525')
                    case _: self.instrument_wid[device_key] = sidu.SerialInstDeviceUi(data_list)
                    
                print(data_list)
                
                self.device_count += 1
            except Exception as e:
                print(f"Failed to instantiate {data_list['name']}: {e}")
                continue
        
        print(self.devices)   
        print("instrument setup done")

    def dataset_setup(self):
        
        self.datasets = {}
        self.datasets['primary'] = Dataset.Dataset() 
        
    def add_windows(self):
    
        for device_key, data_list in self.devices.items():
            model_name = data_list["model"]
            device_name = data_list["name"]
            
            instrument = self.instruments[device_key]
            
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
            widget_instance = widget_class(instrument=instrument, device_info=data_list, device_key=device_key, parent=self)
            
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
            if self.instruments[device_key].connected:
                device_Wid.setEnabled(True)
                initial_function = getattr(device_Wid, f'initialize_widget')
                initial_function()
            else:
                device_Wid.setEnabled(False)
        
        
        # [/]


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
            self.plot_worker = ExperimentController.PlotWorker(self.connected_instuments, self.plot_widgets, self.datasets['primary'].set, self.experiment_period, 
                                        self.pausePushButton, self.experimentNameLineEdit,
                                        self.lockInAmplifier1Wid.xLineEdit, self.lockInAmplifier1Wid.yLineEdit, self.lockInAmplifier1Wid.rLineEdit, self.lockInAmplifier1Wid.thetaLineEdit, 
                                        self.lockInAmplifier2Wid.xLineEdit, self.lockInAmplifier2Wid.yLineEdit, self.lockInAmplifier2Wid.rLineEdit, self.lockInAmplifier2Wid.thetaLineEdit, 
                                        self.temperatureControllerWid.chALineEdit, self.temperatureControllerWid.chBLineEdit, self.temperatureControllerWid.chCLineEdit, self.temperatureControllerWid.chDLineEdit,
                                        self.temperatureControllerWid.chA_line_sub.widget.chALineEdit, self.temperatureControllerWid.chB_line_sub.widget.chBLineEdit, 
                                        self.temperatureControllerWid.chC_line_sub.widget.chCLineEdit, self.temperatureControllerWid.chD_line_sub.widget.chDLineEdit, self.temperatureControllerWid.unitSwitchButton,
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
        
        except Exception as e:
            self.errorDisplay.setText("There's an error. Check the error in the terminal to debug.")
            print(e)
            
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
            except SyntaxError as e: # in case we are opening databases from before the latest version
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
        
        self.serial_inst_create_wid.cancelButton.clicked.connect(self.serial_inst_create_sub.hide)
        self.serial_inst_create_wid.saveButton.clicked.connect(lambda: self.save_device_common(self.serial_inst_create_wid, "serial"))
    
    def gpib_instrument_create(self):
        self.gpib_inst_create_wid = gic.GpibInstCreateUi()
        self.gpib_inst_create_sub = QMdiSubWindow()
        self.mdi.addSubWindow(self.gpib_inst_create_sub)
        
        self.gpib_inst_create_sub.setWidget(self.gpib_inst_create_wid)
        self.gpib_inst_create_sub.setWindowTitle("Add a GPIB Instrument")
        self.gpib_inst_create_sub.resize(570, 470)
        self.gpib_inst_create_sub.move(500, 200)
        
        self.gpib_inst_create_sub.show()
        
        self.gpib_inst_create_wid.cancelButton.clicked.connect(self.gpib_inst_create_sub.hide)
        self.gpib_inst_create_wid.saveButton.clicked.connect(lambda: self.save_device_common(self.gpib_inst_create_wid, "gpib"))
             
    def ethernet_instrument_create(self):
        self.ethernet_inst_create_wid = eic.EthernetInstCreateUi()
        self.ethernet_inst_create_sub = QMdiSubWindow()
        self.mdi.addSubWindow(self.ethernet_inst_create_sub)
        
        self.ethernet_inst_create_sub.setWidget(self.ethernet_inst_create_wid)
        self.ethernet_inst_create_sub.setWindowTitle("Add a GPIB Instrument")
        self.ethernet_inst_create_sub.resize(570, 470)
        self.ethernet_inst_create_sub.move(500, 200)
        
        self.ethernet_inst_create_sub.show()
        
        self.ethernet_inst_create_wid.cancelButton.clicked.connect(self.ethernet_inst_create_sub.hide)
        self.ethernet_inst_create_wid.saveButton.clicked.connect(lambda: self.save_device_common(self.ethernet_inst_create_wid, "ethernet"))
            
    def usb_6525_instrument_create(self):
        self.usb_6525_inst_create_wid = bic.usb6525InstCreateUi()
        self.usb_6525_inst_create_sub = QMdiSubWindow()
        self.mdi.addSubWindow(self.usb_6525_inst_create_sub)
        
        self.usb_6525_inst_create_sub.setWidget(self.usb_6525_inst_create_wid)
        self.usb_6525_inst_create_sub.setWindowTitle("Add a GPIB Instrument")
        self.usb_6525_inst_create_sub.resize(570, 470)
        self.usb_6525_inst_create_sub.move(500, 200)
        
        self.usb_6525_inst_create_sub.show()
        
        self.usb_6525_inst_create_wid.cancelButton.clicked.connect(self.usb_6525_inst_create_sub.hide)
        self.usb_6525_inst_create_wid.saveButton.clicked.connect(lambda: self.save_device_common(self.usb_6525_inst_create_wid, "usb6525"))
        
    def save_device_common(self, creator_widget, interface_type):
        creator_widget.update_parameters()
        data_list = creator_widget.data_list

        # --- Save instrument script ---
        script_dir = "C:/Users/szkop/OneDrive/Desktop/YonKu/Tools/saved_instruments"
        file_name = f"{data_list['model']}.py"
        full_path = os.path.join(script_dir, file_name)

        os.makedirs(script_dir, exist_ok=True)

        with open(full_path, "w") as f:
            f.write(creator_widget.device_script())

        # --- Reload metadata ---
        with open(full_path, "r") as f:
            content = f.readline().strip().strip("#")
            data_list = eval(content)   # replace later with safer parsing

        # --- Register device ---
        device_key = f"Device_{self.device_count}"
        self.devices[device_key] = data_list

        # Create device UI (tab view)
        ui_class_map = {
            "serial": sidu.SerialInstDeviceUi,
            "gpib": gidu.GPIBInstDeviceUi,
            "ethernet": eidu.EthernetInstDeviceUi,
            "usb6525": uidu.usb6525InstDeviceUi,
        }

        self.instrument_wid[device_key] = ui_class_map[interface_type](data_list)

        # --- Instantiate instrument ---
        self.instantiate_device(data_list, device_key, interface_type)

        # --- Add to device list tab ---
        self.deviceListSub.widget.tabWidget.addTab(self.instrument_wid[device_key], device_key)

        self.device_count += 1

        # --- Generate UI + widget files ---
        self.create_generated_files(creator_widget)
    
    def instantiate_device(self, data_list, device_key, interface_type):
        model_name = data_list["model"]
        device_name = data_list["name"]

        module_path = f"Tools.saved_instruments.{model_name}"

        try:
            module = importlib.import_module(module_path)
            cls = getattr(module, device_name)
        except Exception as e:
            print(f"[ERROR] import failed: {e}")
            return

        try:
            match interface_type:
                case "serial":
                    inst = cls(device_name, data_list["port"])

                case "gpib":
                    inst = cls(device_name, data_list["address"])

                case "ethernet":
                    inst = cls(device_name, data_list["instIP"], int(data_list["port"]))

                case "usb6525":
                    inst = cls(
                        device_name,
                        f"Dev{data_list['deviceNumber']}",
                        f"port{data_list['port']}",
                        f"line{data_list['range1']}:{data_list['range2']}"
                    )

                case _:
                    raise ValueError("Unknown interface")

        except Exception as e:
            print(f"[ERROR] instantiation failed: {e}")
            return

        # store instrument (⚠️ still model-keyed for now)
        self.instruments[device_key] = inst

        # update UI connection state
        wid = self.instrument_wid[device_key]
        wid.instrument = inst

        if inst.connected:
            wid.connectionLineEdit.setText("Connected")
        else:
            wid.connectionLineEdit.setText("Not Connected")

    def create_generated_files(self, creator_widget):
        model = creator_widget.data_list["model"]

        base_ui_dir = "C:/Users/szkop/OneDrive/Desktop/YonKu/GUI/ui_files/instrument_control_uis"
        base_widget_dir = "C:/Users/szkop/OneDrive/Desktop/YonKu/GUI/instrument_control_widgets"

        os.makedirs(base_ui_dir, exist_ok=True)
        os.makedirs(base_widget_dir, exist_ok=True)

        # --- UI file ---
        ui_path = os.path.join(base_ui_dir, f"{model}_ui.ui")
        with open(ui_path, "w") as f:
            f.write(creator_widget.device_ui_script())

        # --- JSON config ---
        json_path = os.path.join(base_ui_dir, f"{model}_ui.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4)

        # --- widget python file ---
        widget_path = os.path.join(base_widget_dir, f"{model}_widget.py")
        with open(widget_path, "w") as f:
            f.write(creator_widget.device_wid_script())
            

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
            
            for device_key, device in self.instruments.items():
                self.instruments[device_key].close()
            
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
        
"""Exception Handler"""
class ExceptionForwarder(QObject):
    exception_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def handle_exception(self, exc_type, exc_value, exc_tb):
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        print(error_msg)
        self.exception_occurred.emit(error_msg)
      
      
if __name__ == "__main__":
    app = QApplication(sys.argv)
    UIWindow = UI()
    app.exec()
    
    
    