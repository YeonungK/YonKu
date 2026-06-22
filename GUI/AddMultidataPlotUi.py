from pathlib import Path

from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget, QFileDialog
from PyQt5 import uic, QtCore
import sys
import pandas as pd

from Tools.ExperimentParameters import load_experiment_parameters
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
                self.expParam = load_experiment_parameters(self.experimentParamLink)

                available_data_types = list(dataset.columns.get_level_values(0).unique())

                self.xAxis_exists = self.xAxis in available_data_types
                self.yAxis_exists = self.yAxis in available_data_types

                
                
                # # check if the dataset includes the xaxis and yaxis data type
                # except SyntaxError: # in case we are opening databases from before the latest version
                
                
                
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

    

        
    