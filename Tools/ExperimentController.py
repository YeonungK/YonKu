from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from Tools import DataLogger
from Tools.saved_instruments.Oxford_MercuryiPS import instrument as magnetPowerSupply

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
        for device_key, instrument in self.instruments.items():
            if not instrument.data_type:
                self.omitted_instruments.append(device_key)
            if isinstance(instrument, magnetPowerSupply.magnetPowerSupply):
                self.omitted_instruments.append(device_key)
        
        for device_key in self.omitted_instruments:
            del self.instruments[device_key]
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
        