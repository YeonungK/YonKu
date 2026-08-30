from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from Tools import DataLogger
from Tools.saved_instruments.Oxford_MercuryiPS import instrument as magnetPowerSupply
from Tools.saved_instruments.INFICON_VGC401 import instrument as pressureGauge
from Tools.ExperimentSchema import build_experiment_schema
import json
from project_paths import EXPERIMENT_PARAMETERS_DIR

"""worker class for Expriments and Real-time Plotting (thread)"""
class PlotWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal()
    update = pyqtSignal()
    measurement_ready = pyqtSignal(str, str, str, object)

    def __init__(self, instruments, plot_widgets, dataset, period, pausePushButton, 
                 titleLineEdit, xLineEdit, yLineEdit, rLineEdit, thetaLineEdit,
                 xLineEdit2, yLineEdit2, rLineEdit2, thetaLineEdit2, 
                 chALineEdit, chBLineEdit, chCLineEdit, chDLineEdit,
                 chABigLine, chBBigLine, chCBigLine, chDBigLine, unitButton,
                 magnetzLineEdit, currentLineEdit, experimentSettingWid):
        
        super().__init__()

        self.instruments = {}

        for device_key, instrument in instruments.items():
            if not getattr(instrument, "data_type", {}):
                continue

            if not getattr(instrument, "data_function", {}):
                continue
        
            self.instruments[device_key] = instrument
        
        print("Acquirable instruments:", self.instruments)
        
        # self.instruments = instruments
        # self.omitted_instruments = []
        # for device_key, instrument in self.instruments.items():
        #     if not instrument.data_type:
        #         self.omitted_instruments.append(device_key)
        #     if isinstance(instrument, pressureGauge.pressureGauge):
        #         self.omitted_instruments.append(device_key)
        
        # for device_key in self.omitted_instruments:
        #     del self.instruments[device_key]
        # print(self.instruments)
        
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

        self.file_path = EXPERIMENT_PARAMETERS_DIR / f"{self.experiment_title}.json"

        self.experimentSettingWid.save_all_values()
        params = self.experimentSettingWid.experiment_parameters

        # --- Metadata ---
        metadata = {
            "start_datetime": self.experiment_datetime,
            "name": self.experiment_name,
            "measurement_period_ms": self.period
        }

        # --- Data schema ---
        schema_info = build_experiment_schema(
            self.instruments,
            self.experimentSettingWid
        )
        # def add_group(group_name, keys):
        #     for key in keys:
        #         name = params[f"{group_name}_name"][key]
        #         unit = params.get(f"{group_name}_unit", {}).get(key, "")

        #         schema_key = f"{group_name}_{key}"
        #         data_schema[schema_key] = {
        #             "label": name,
        #             "unit": unit
        #         }

        # # Temperature
        # add_group("temperature", ["ch_A", "ch_B", "ch_C", "ch_D"])

        # # Resistance
        # add_group("resistance", ["ch_A", "ch_B", "ch_C", "ch_D"])

        # # Lock-in 1
        # add_group("lockIn", ["x", "y", "r", "theta"])

        # # Lock-in 2
        # add_group("lockIn2", ["x", "y", "r", "theta"])

        # # Single values
        # data_schema["field"] = {
        #     "label": params["field_name"]["field"],
        #     "unit": params["field_unit"]["field"]
        # }

        # data_schema["current"] = {
        #     "label": params["current_name"]["current"],
        #     "unit": params["current_unit"]["current"]
        # }

        # data_schema["time"] = {
        #     "label": params["time_name"]["time"],
        #     "unit": "s"
        # }


        # --- Final structure ---
        experiment_json = {
            "metadata": metadata,
            "devices": schema_info["devices"],
            "available_data_types": schema_info["available_data_types"],
            "data_schema": schema_info["data_schema"],
            "pause_times": [],
            "resume_times": [],
            "end_time": None
        }

        # --- Save ---
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(experiment_json, f, indent=4)
        
#     def log_experiment_parameters(self):

#         self.file_path = Path(f"C:/Users/szkop/OneDrive/Desktop/YonKu/Data/experiment_parameters/{self.experiment_title}.txt")
#         self.experimentSettingWid.save_all_values()
        
#         self.experiment_parameters = f"""startDatetime:{self.experiment_datetime}
# name:{self.experiment_name}
# measurementPeriod:{self.period}


# temperature_ch_A_name:{self.experimentSettingWid.experiment_parameters['temperature_name']['ch_A']}
# temperature_ch_B_name:{self.experimentSettingWid.experiment_parameters['temperature_name']['ch_B']}
# temperature_ch_C_name:{self.experimentSettingWid.experiment_parameters['temperature_name']['ch_C']}
# temperature_ch_D_name:{self.experimentSettingWid.experiment_parameters['temperature_name']['ch_D']}

# temperature_ch_A_unit:{self.experimentSettingWid.experiment_parameters['temperature_unit']['ch_A']}
# temperature_ch_B_unit:{self.experimentSettingWid.experiment_parameters['temperature_unit']['ch_B']}
# temperature_ch_C_unit:{self.experimentSettingWid.experiment_parameters['temperature_unit']['ch_C']}
# temperature_ch_D_unit:{self.experimentSettingWid.experiment_parameters['temperature_unit']['ch_D']}


# resistance_ch_A_name:{self.experimentSettingWid.experiment_parameters['resistance_name']['ch_A']}
# resistance_ch_B_name:{self.experimentSettingWid.experiment_parameters['resistance_name']['ch_B']}
# resistance_ch_C_name:{self.experimentSettingWid.experiment_parameters['resistance_name']['ch_C']}
# resistance_ch_D_name:{self.experimentSettingWid.experiment_parameters['resistance_name']['ch_D']}

# resistance_ch_A_unit:{self.experimentSettingWid.experiment_parameters['resistance_unit']['ch_A']}
# resistance_ch_B_unit:{self.experimentSettingWid.experiment_parameters['resistance_unit']['ch_B']}
# resistance_ch_C_unit:{self.experimentSettingWid.experiment_parameters['resistance_unit']['ch_C']}
# resistance_ch_D_unit:{self.experimentSettingWid.experiment_parameters['resistance_unit']['ch_D']}


# lockIn_x_name:{self.experimentSettingWid.experiment_parameters['lockIn_name']['x']}
# lockIn_y_name:{self.experimentSettingWid.experiment_parameters['lockIn_name']['y']}
# lockIn_r_name:{self.experimentSettingWid.experiment_parameters['lockIn_name']['r']}
# lockIn_theta_name:{self.experimentSettingWid.experiment_parameters['lockIn_name']['theta']}

# lockIn_x_unit:{self.experimentSettingWid.experiment_parameters['lockIn_unit']['x']}
# lockIn_y_unit:{self.experimentSettingWid.experiment_parameters['lockIn_unit']['y']}
# lockIn_r_unit:{self.experimentSettingWid.experiment_parameters['lockIn_unit']['r']}
# lockIn_theta_unit:{self.experimentSettingWid.experiment_parameters['lockIn_unit']['theta']}


# lockIn2_x_name:{self.experimentSettingWid.experiment_parameters['lockIn2_name']['x']}
# lockIn2_y_name:{self.experimentSettingWid.experiment_parameters['lockIn2_name']['y']}
# lockIn2_r_name:{self.experimentSettingWid.experiment_parameters['lockIn2_name']['r']}
# lockIn2_theta_name:{self.experimentSettingWid.experiment_parameters['lockIn2_name']['theta']}

# lockIn2_x_unit:{self.experimentSettingWid.experiment_parameters['lockIn2_unit']['x']}
# lockIn2_y_unit:{self.experimentSettingWid.experiment_parameters['lockIn2_unit']['y']}
# lockIn2_r_unit:{self.experimentSettingWid.experiment_parameters['lockIn2_unit']['r']}
# lockIn2_theta_unit:{self.experimentSettingWid.experiment_parameters['lockIn2_unit']['theta']}


# field_name:{self.experimentSettingWid.experiment_parameters['field_name']['field']}
# field_unit:{self.experimentSettingWid.experiment_parameters['field_unit']['field']}


# current_name:{self.experimentSettingWid.experiment_parameters['current_name']['current']}
# current_unit:{self.experimentSettingWid.experiment_parameters['current_unit']['current']}


# time_name:{self.experimentSettingWid.experiment_parameters['time_name']['time']}

# {list(self.instruments.keys())}\n"""
        
        
#         with open(self.file_path, "w") as f:
#             f.write(self.experiment_parameters)
#             f.close()
    

            
    def plot_update(self):
    
        self.instrument_read_data()
        
        self.update.emit()
        
        # for index, plt_wid in self.plot_widgets.items():
        #     if isinstance(plt_wid, PlotUi.plotWidget):
        #         plt_wid.plot_data()
    
    def instrument_read_data(self):
        
        self.logging_data_list = []
        
        for device_key, instrument in self.instruments.items():
            for data_type, function in instrument.data_function.items():

                channels = instrument.data_type.get(data_type, [])

                try:
                    values = function()
                except Exception as e:
                    print(f"Error reading {device_key} / {data_type}: {e}")
                    values = None

                if values is None:
                    values = [0] * len(channels)

                elif not isinstance(values, (list, tuple)):
                    values = [values]

                if len(values) != len(channels):
                    print(
                        f"Warning: {device_key} / {data_type} returned "
                        f"{len(values)} values for {len(channels)} channels."
                    )
                    values = [0] * len(channels)
                
                self.logging_data_list.append(values)

                for channel, value in zip(channels, values):
                    self.dataset[data_type][channel].append(value)
                    self.measurement_ready.emit(device_key, data_type, channel, value)

                # Compatibility bridge for legacy, model-specific widgets.
                self.update_known_widget_fields(data_type, values)
            
            
        now = datetime.now(ZoneInfo('America/New_York')).timestamp()
        self.dataset['time']['time'].append(now)
        
        self.logging_data_list.append([now])
        print("------------------------")   
        print(self.logging_data_list)
        print("------------------------")
        self.logger.append(self.logging_data_list)     
    
    def update_known_widget_fields(self, data_type, values):
        """
        Temporary compatibility layer.

        Long-term, widget updates should be handled by each instrument widget,
        not hardcoded here.
        """

        if data_type == "temperature":
            if len(values) >= 4:
                self.chALineEdit.setText(str(values[0]))
                self.chBLineEdit.setText(str(values[1]))
                self.chCLineEdit.setText(str(values[2]))
                self.chDLineEdit.setText(str(values[3]))

                self.chABigLine.setText(str(values[0]))
                self.chBBigLine.setText(str(values[1]))
                self.chCBigLine.setText(str(values[2]))
                self.chDBigLine.setText(str(values[3]))

        elif data_type == "lockIn":
            if len(values) >= 4:
                self.xLineEdit.setText(str(values[0]))
                self.yLineEdit.setText(str(values[1]))
                self.rLineEdit.setText(str(values[2]))
                self.thetaLineEdit.setText(str(values[3]))

        elif data_type == "lockIn2":
            if len(values) >= 4:
                self.xLineEdit2.setText(str(values[0]))
                self.yLineEdit2.setText(str(values[1]))
                self.rLineEdit2.setText(str(values[2]))
                self.thetaLineEdit2.setText(str(values[3]))

        elif data_type == "field":
            if len(values) >= 1:
                self.magnetzLineEdit.setText(str(values[0]))

        elif data_type == "current":
            if len(values) >= 1:
                self.currentLineEdit.setText(str(values[0]))
    
        
    def pause_resume_experiment(self):
        if self.pausePushButton.isChecked():
            self.timer.stop()
            pauseTime = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
            # 1. Load existing data
            with open(self.file_path, "r") as f:
                data = json.load(f)
            # 2. Modify it  
            data["pause_times"].append(pauseTime)   # append to list
            # 3. Save back
            with open(self.file_path, "w") as f:
                json.dump(data, f, indent=4)
        else:
            resumeTime = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
            # 1. Load existing data
            with open(self.file_path, "r") as f:
                data = json.load(f)
            # 2. Modify it  
            data["resume_times"].append(resumeTime)   # append to list
            # 3. Save back
            with open(self.file_path, "w") as f:
                json.dump(data, f, indent=4)
            self.timer = QTimer()
            self.timer.timeout.connect(self.plot_update)
            self.timer.start(self.period) 
    
    def end_experiment(self):
        self.timer.stop()
        
        endTime = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
        # 1. Load existing data
        with open(self.file_path, "r") as f:
            data = json.load(f)
        # 2. Modify it  
        data["end_time"] = endTime  # append to list
        # 3. Save back
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)
        
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
