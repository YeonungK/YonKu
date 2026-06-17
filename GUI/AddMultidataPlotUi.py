import ast
import json
from pathlib import Path

from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget, QFileDialog
from PyQt5 import uic, QtCore
import sys
import pandas as pd

from project_paths import GUI_DIR, EXPERIMENT_DATA_DIR, EXPERIMENT_PARAMETERS_DIR



class add_multidata_plot_ui(QWidget):
    def __init__(self, xAxis, yAxis, xAxis_name_key, yAxis_name_key, xAxis_unit_key, yAxis_unit_key, xData, yData, experiment_parameters):
        super().__init__()

        uic.loadUi(f"{GUI_DIR}/ui_files/add_multidata_plot.ui", self)
        
        self.add_signal = QtCore.pyqtSignal()
        
        self.xAxis = xAxis
        self.yAxis = yAxis
        
        self.xAxis_name_key = xAxis_name_key
        self.yAxis_name_key = yAxis_name_key
        
        self.xAxis_unit_key = xAxis_unit_key
        self.yAxis_unit_key = yAxis_unit_key
        
        self.xData = xData
        self.yData = yData
        
        self.plot_experiment_parameters = experiment_parameters
        
        self.x_channel_list = list(self.xData.keys())
        self.y_channel_list = list(self.yData.keys())
        


        self.experimentParamLink = ""
        self.BrowseDatasetButton.clicked.connect(self.dataset_search)

      
    def load_experiment_parameters(self, param_path):
        """
        Supports both:
        - new .json experiment parameter files
        - old .txt experiment parameter files
        """
        param_path = Path(param_path)
        base = param_path.with_suffix("")  # remove extension


        for ext in [".json", ".txt"]:
            file_path = base.with_suffix(ext)
            if file_path.exists():
                param_path = file_path
                break
            else:
                return {
            "format": "legacy_txt",
            "metadata": {
                "start_datetime": "",
                "name": "",
                "measurement_period_ms": ""
            },
            "data_schema": {
                "temperature_ch_A": {
                    "label": "Ch_A",
                    "unit": "K"    
                },
                "temperature_ch_B": {
                    "label": "Ch_B",
                    "unit": "K"
                },
                "temperature_ch_C": {
                    "label": "Ch_C",
                    "unit": "K"
                },
                "temperature_ch_D": {
                    "label": "Ch_D",
                    "unit": "K"
                },
                "resistance_ch_A": {
                    "label": "Ch_A",
                    "unit": "Ohms"
                },
                "resistance_ch_B": {
                    "label": "Ch_B",
                    "unit": "Ohms"
                },
                "resistance_ch_C": {
                    "label": "Ch_C",
                    "unit": "Ohms"
                },
                "resistance_ch_D": {
                    "label": "Ch_D",
                    "unit": "Ohms"
                },
                "lockIn_x": {
                    "label": "X",
                    "unit": "manual"
                },
                "lockIn_y": {
                    "label": "Y",
                    "unit": "manual"
                },
                "lockIn_r": {
                    "label": "R",
                    "unit": "manual"
                },
                "lockIn_theta": {
                    "label": "Theta",
                    "unit": "degrees"   
                },
                "lockIn2_x": {
                    "label": "X",
                    "unit": "manual"
                },
                "lockIn2_y": {
                    "label": "Y",
                    "unit": "manual"
                },
                "lockIn2_r": {
                    "label": "R",
                    "unit": "manual"
                },
                "lockIn2_theta": {
                    "label": "Theta",
                    "unit": "degrees"
                },
                "field": {
                    "label": "field",
                    "unit": "T"
                },
                "current": {
                    "label": "current",
                    "unit": "A"
                },
                "time": {
                    "label": "time",
                    "unit": "s"
                }
            },
            "connected_models": ['Lakeshore_336', 'Oxford_MercuryiPS', 'SRS_830', 'SRS_830_2'],
            "available_data_types": ['time','temperature', 'resistance', 'lockIn', 'lockIn2', 'field', 'current']
        }

        if param_path.suffix.lower() == ".json":
            with open(param_path, "r", encoding="utf-8") as f:
                return json.load(f)

        if param_path.suffix.lower() == ".txt":
            return self.parse_old_txt_experiment_parameters(param_path)

        raise ValueError(f"Unsupported parameter file type: {param_path.suffix}")

    def parse_old_txt_experiment_parameters(self, param_path):
        """
        Converts old text parameter files into a normalized dictionary.
        """
        params = {}
        connected_models = []
        available_data_types = ['time']

        with open(param_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                # old connected instruments line:
                # ['Lakeshore_336', 'Oxford_MercuryiPS', 'SRS_830_2']
                if line.startswith("[") and line.endswith("]"):
                    try:
                        connected_models = ast.literal_eval(line)
                    except Exception:
                        connected_models = ['Lakeshore_336', 'Oxford_MercuryiPS', 'SRS_830', 'SRS_830_2']
                    continue


                if ":" in line:
                    key, value = line.split(":", 1)
                    params[key.strip()] = value.strip()
            
        for model in connected_models:
                match model:
                    case 'Lakeshore_336':
                        available_data_types.extend(['temperature', 'resistance'])
                    case 'Oxford_MercuryiPS':
                        available_data_types.extend(['field', 'current'])
                    case 'SRS_830':
                        available_data_types.extend(['lockIn'])
                    case 'SRS_830_2':
                        available_data_types.extend(['lockIn2'])
                
                

        return {
            "format": "legacy_txt",
            "metadata": {
                "start_datetime": params.get("startDatetime", ""),
                "name": params.get("name", ""),
                "measurement_period_ms": params.get("measurementPeriod", "")
            },
            "data_schema": {
                "temperature_ch_A": {
                    "label": params.get("temperature_ch_A_label", "Ch_A"),
                    "unit": params.get("temperature_ch_A_unit", "K")    
                },
                "temperature_ch_B": {
                    "label": params.get("temperature_ch_B_label", "Ch_B"),
                    "unit": params.get("temperature_ch_B_unit", "K")
                },
                "temperature_ch_C": {
                    "label": params.get("temperature_ch_C_label", "Ch_C"),
                    "unit": params.get("temperature_ch_C_unit", "K")
                },
                "temperature_ch_D": {
                    "label": params.get("temperature_ch_D_label", "Ch_D"),
                    "unit": params.get("temperature_ch_D_unit", "K")
                },
                "resistance_ch_A": {
                    "label": params.get("resistance_ch_A_label", "Ch_A"),
                    "unit": params.get("resistance_ch_A_unit", "Ohms")
                },
                "resistance_ch_B": {
                    "label": params.get("resistance_ch_B_label", "Ch_B"),
                    "unit": params.get("resistance_ch_B_unit", "Ohms")
                },
                "resistance_ch_C": {
                    "label": params.get("resistance_ch_C_label", "Ch_C"),
                    "unit": params.get("resistance_ch_C_unit", "Ohms")
                },
                "resistance_ch_D": {
                    "label": params.get("resistance_ch_D_label", "Ch_D"),
                    "unit": params.get("resistance_ch_D_unit", "Ohms")
                },
                "lockIn_x": {
                    "label": params.get("lockIn_x_label", "X"),
                    "unit": params.get("lockIn_x_unit", "manual")
                },
                "lockIn_y": {
                    "label": params.get("lockIn_y_label", "Y"),
                    "unit": params.get("lockIn_y_unit", "manual")
                },
                "lockIn_r": {
                    "label": params.get("lockIn_r_label", "R"),
                    "unit": params.get("lockIn_r_unit", "manual")
                },
                "lockIn_theta": {
                    "label": params.get("lockIn_theta_label", "Theta"),
                    "unit": params.get("lockIn_theta_unit", "degrees")   
                },
                "lockIn2_x": {
                    "label": params.get("lockIn2_x_label", "X"),
                    "unit": params.get("lockIn2_x_unit", "manual")
                },
                "lockIn2_y": {
                    "label": params.get("lockIn2_y_label", "Y"),
                    "unit": params.get("lockIn2_y_unit", "manual")
                },
                "lockIn2_r": {
                    "label": params.get("lockIn2_r_label", "R"),
                    "unit": params.get("lockIn2_r_unit", "manual")
                },
                "lockIn2_theta": {
                    "label": params.get("lockIn2_theta_label", "Theta"),
                    "unit": params.get("lockIn2_theta_unit", "degrees")
                },
                "field": {
                    "label": params.get("field_label", "field"),
                    "unit": params.get("field_unit", "T")
                },
                "current": {
                    "label": params.get("current_label", "current"),
                    "unit": params.get("current_unit", "A")
                },
                "time": {
                    "label": params.get("time_label", "time"),
                    "unit": params.get("time_unit", "s")
                }
            },
            "connected_models": connected_models,
            "available_data_types": available_data_types
        }


    def dataset_search(self):
        self.xAxis_exists = False
        self.yAxis_exists = False

        # find the experiment parameters file link
        fname = QFileDialog.getOpenFileName(self, "Open File", str(EXPERIMENT_DATA_DIR), "CSV Files (*.csv)")
        
        if fname[0]:  # if the user selects a file
            try:
                
                self.datasetLink = Path(fname[0])

                dataset = pd.read_csv(self.datasetLink, header=[0,1])
                # go to experiment_parameters folder and keep same filename
                param_base = EXPERIMENT_PARAMETERS_DIR / self.datasetLink.stem

                self.experimentParamLink = str(param_base)
                            
                self.expParam = self.load_experiment_parameters(
                self.experimentParamLink
            )

                available_data_types = list(dataset.columns.get_level_values(0).unique())

                self.xAxis_exists = self.xAxis in available_data_types
                self.yAxis_exists = self.yAxis in available_data_types

                
                
                # # check if the dataset includes the xaxis and yaxis data type
                # try:
                #     param_file = open(self.experimentParamLink)    
                #     param_file_content = param_file.readlines()
                #     connected_instruments = eval(param_file_content[59].replace("\n",""))
                #     print(connected_instruments)
                # except SyntaxError: # in case we are opening databases from before the latest version
                #     print(e)
                #     connected_instruments = ['Lakeshore_336', 'Oxford_MercuryiPS', 'SRS_830', 'SRS_830_2']
                # except FileNotFoundError as e:
                #     print(e)
                #     print("Error detected at the nested level")
                #     connected_instruments = ['Lakeshore_336', 'Oxford_MercuryiPS', 'SRS_830', 'SRS_830_2']
                # except UnboundLocalError as e:
                #     print(e)
                #     connected_instruments = ['Lakeshore_336', 'Oxford_MercuryiPS', 'SRS_830', 'SRS_830_2']
                
                # for instrument in connected_instruments:
                #     for data_type in list(self.instruments[instrument].data_type.keys()):
                #         print(data_type)
                #         if data_type == self.xAxis:
                #             self.xAxis_exists = True
                #         if data_type == self.yAxis:
                #             self.yAxis_exists = True
                #         print([self.xAxis_exists,self.yAxis_exists])
                
                # if self.xAxis == 'time':
                #     self.xAxis_exists = True
                # if self.yAxis == 'time':
                #     self.yAxis_exists = True
                
                # if they do, proceed to set names in the 
                if self.xAxis_exists and self.yAxis_exists:
                    self.AxisDatasetLineEdit.setText(fname[0])
                    self.datasetLink = fname[0]
                    self.x_channel_list = list(dataset[self.xAxis].columns)
                    self.y_channel_list = list(dataset[self.yAxis].columns)

                    self.set_names()
                    
                else:
                    print(self.xAxis, self.yAxis)
                    self.AxisDatasetLineEdit.setText("This dataset doesn't include the chosen data types.")
                
            except IndexError:
                pass
        else: pass
            
        
    def set_names(self):
        
        self.xAxisChannelComboBox.clear()
        self.yAxisChannelComboBox.clear()

        # Populate X-axis channel combo box
        for ch in self.x_channel_list:
            label = self.expParam.get("data_schema", {}).get(
                f"{self.xAxis}_{ch}",
                {}
            ).get("label", ch)

            self.xAxisChannelComboBox.addItem(label)

        # Populate Y-axis channel combo box
        for ch in self.y_channel_list:
            label = self.expParam.get("data_schema", {}).get(
                f"{self.yAxis}_{ch}",
                {}
            ).get("label", ch)

            self.yAxisChannelComboBox.addItem(label)

    
    def update_data(
        self,
        datasetLink,
        channel_list,
        comboBox,
        empty_set,
        axis,
        empty_experiment_parameters,
        full_experiment_parameters,
        name_key=None,
        unit_key=None
    ):
        dataset = pd.read_csv(datasetLink, header=[0, 1])

        axis_channel = channel_list[comboBox.currentIndex()]
        axis_name = self.plotNameLineEdit.text() + "_" + comboBox.currentText()

        try:
            empty_set[axis_name] = dataset[(axis, axis_channel)].to_list()
        except KeyError:
            self.AxisDatasetLineEdit.setText("This dataset doesn't contain the chosen data types.")
            return None

        empty_experiment_parameters.setdefault("data_schema", {})

        source_key = f"{axis}_{axis_channel}"
        target_key = f"{axis}_{axis_name}"

        source_schema = full_experiment_parameters.get("data_schema", {}).get(
            source_key,
            {
                "label": axis_channel,
                "unit": "-"
            }
        )

        print(source_schema)

        empty_experiment_parameters["data_schema"][target_key] = source_schema

        try:
            return axis_name, source_schema["unit"]
        except KeyError:
            return axis_name, "-"

    

        
    