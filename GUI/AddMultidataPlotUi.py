from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget, QFileDialog
from PyQt5 import uic, QtCore
import sys
import pandas as pd



class add_multidata_plot_ui(QWidget):
    def __init__(self, xAxis, yAxis, xAxis_name_key, yAxis_name_key, xAxis_unit_key, yAxis_unit_key, xData, yData, experiment_parameters):
        super().__init__()

        uic.loadUi("GUI/ui_files/add_multidata_plot.ui", self)
        
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
        self.xBrowseDatasetButton.clicked.connect(self.x_dataset_search)
        self.yBrowseDatasetButton.clicked.connect(self.y_dataset_search)

        
        
    def x_dataset_search(self):
        
        try:
            x_fname = QFileDialog.getOpenFileName(self, "Open File", "C:/Users/szkop/Desktop/YonKu_Editing/Data/experiment_data", "CSV Files (*.csv)")
            self.x_datasetLink = x_fname[0]
            self.x_paramLink = self.x_datasetLink[:-3] + "txt"
            self.x_paramLink = self.x_paramLink.split("/")
            
            self.x_paramLink[6] = "experiment_parameters"
            
            self.x_experimentParamLink = self.x_paramLink[0]
            
            for n in range(1,8):
                self.x_experimentParamLink = self.x_experimentParamLink + "/" + self.x_paramLink[n]
                print(self.x_experimentParamLink)
                
            if x_fname:
                self.xAxisDatasetLineEdit.setText(x_fname[0])
                self.x_datasetLink = x_fname[0]
                self.x_expParam = self.set_names(self.x_experimentParamLink, self.xAxisChannelComboBox, self.xAxis_name_key, self.xData)
                print(f"x_parameter: {self.x_expParam}")
            else:
                pass
            
        except IndexError:
            pass
            
        
        
    def y_dataset_search(self):
        
        try:
            y_fname = QFileDialog.getOpenFileName(self, "Open File", "C:/Users/szkop/Desktop/YonKu_Editing/Data/experiment_data", "CSV Files (*.csv)")
            
            self.y_datasetLink = y_fname[0]
            self.y_paramLink = self.y_datasetLink[:-3] + "txt"
            self.y_paramLink = self.y_paramLink.split("/")
            
            self.y_paramLink[6] = "experiment_parameters"
            
            self.y_experimentParamLink = self.y_paramLink[0]
            
            for n in range(1,8):
                self.y_experimentParamLink = self.y_experimentParamLink + "/" + self.y_paramLink[n]
                print(self.y_experimentParamLink)
            if y_fname:
                self.yAxisDatasetLineEdit.setText(y_fname[0])
                self.y_datasetLink = y_fname[0]
                self.y_expParam = self.set_names(self.y_experimentParamLink, self.yAxisChannelComboBox, self.yAxis_name_key, self.yData)
                print(f"y_parameter: {self.y_expParam}")
            else:
                pass
        
        except IndexError:
            pass
        
    def set_names(self, experimentParamLink, combo_box, name_key, data):
        
        try:
            param_file = open(experimentParamLink)
                    
            param_file_list = param_file.readlines()
            
            print(param_file_list)
            
            experiment_parameters = {'temperatures_name':{"ch_A":"Ch_A","ch_B":"Ch_B","ch_C":"Ch_C","ch_D":"Ch_D"}, 'temperatures_unit':{"ch_A":"K","ch_B":"K","ch_C":"K","ch_D":"K"},
                                        'resistances_name':{"ch_A":"Ch_A","ch_B":"Ch_B","ch_C":"Ch_C","ch_D":"Ch_D"}, 'resistances_unit':{"ch_A":"Ohms","ch_B":"Ohms","ch_C":"Ohms","ch_D":"Ohms"},
                                        'lockIn_name':{"x":"X","y":"Y","r":"R","theta":"Theta"}, 'lockIn_unit':{"x":"manual","y":"manual","r":"manual","theta":"degrees"},
                                        'lockIn2_name':{"x":"X","y":"Y","r":"R","theta":"Theta"}, 'lockIn2_unit':{"x":"manual","y":"manual","r":"manual","theta":"degrees"},
                                        'fields_name':{"field":"field"}, 'fields_unit':{"field":"T"},
                                        'currents_name':{"current":"current"}, 'currents_unit':{"current":"A"},
                                        'times_name':{"time":"time"}}
            
            experiment_parameters['temperatures_name']["ch_A"] = param_file_list[5].split(":")[1].replace("\n","")
            experiment_parameters['temperatures_name']["ch_B"] = param_file_list[6].split(":")[1].replace("\n","")
            experiment_parameters['temperatures_name']["ch_C"] = param_file_list[7].split(":")[1].replace("\n","")
            experiment_parameters['temperatures_name']["ch_D"] = param_file_list[8].split(":")[1].replace("\n","")
            
            experiment_parameters['temperatures_unit']["ch_A"] = param_file_list[10].split(":")[1].replace("\n","")
            experiment_parameters['temperatures_unit']["ch_B"] = param_file_list[11].split(":")[1].replace("\n","")
            experiment_parameters['temperatures_unit']["ch_C"] = param_file_list[12].split(":")[1].replace("\n","")
            experiment_parameters['temperatures_unit']["ch_D"] = param_file_list[13].split(":")[1].replace("\n","")
            
            experiment_parameters['resistances_name']["ch_A"] = param_file_list[16].split(":")[1].replace("\n","")
            experiment_parameters['resistances_name']["ch_B"] = param_file_list[17].split(":")[1].replace("\n","")
            experiment_parameters['resistances_name']["ch_C"] = param_file_list[18].split(":")[1].replace("\n","")
            experiment_parameters['resistances_name']["ch_D"] = param_file_list[19].split(":")[1].replace("\n","")
            
            experiment_parameters['resistances_unit']["ch_A"] = param_file_list[21].split(":")[1].replace("\n","")
            experiment_parameters['resistances_unit']["ch_B"] = param_file_list[22].split(":")[1].replace("\n","")
            experiment_parameters['resistances_unit']["ch_C"] = param_file_list[23].split(":")[1].replace("\n","")
            experiment_parameters['resistances_unit']["ch_D"] = param_file_list[24].split(":")[1].replace("\n","")

            experiment_parameters['lockIn_name']["x"] = param_file_list[27].split(":")[1].replace("\n","")
            experiment_parameters['lockIn_name']["y"] = param_file_list[28].split(":")[1].replace("\n","")
            experiment_parameters['lockIn_name']["r"] = param_file_list[29].split(":")[1].replace("\n","")
            experiment_parameters['lockIn_name']["theta"] = param_file_list[30].split(":")[1].replace("\n","")
            
            experiment_parameters['lockIn_unit']["x"] = param_file_list[32].split(":")[1].replace("\n","")
            experiment_parameters['lockIn_unit']["y"] = param_file_list[33].split(":")[1].replace("\n","")
            experiment_parameters['lockIn_unit']["r"] = param_file_list[34].split(":")[1].replace("\n","")
            experiment_parameters['lockIn_unit']["theta"] = param_file_list[35].split(":")[1].replace("\n","")
            
            experiment_parameters['lockIn2_name']["x"] = param_file_list[38].split(":")[1].replace("\n","")
            experiment_parameters['lockIn2_name']["y"] = param_file_list[39].split(":")[1].replace("\n","")
            experiment_parameters['lockIn2_name']["r"] = param_file_list[40].split(":")[1].replace("\n","")
            experiment_parameters['lockIn2_name']["theta"] = param_file_list[41].split(":")[1].replace("\n","")
            
            experiment_parameters['lockIn2_unit']["x"] = param_file_list[43].split(":")[1].replace("\n","")
            experiment_parameters['lockIn2_unit']["y"] = param_file_list[44].split(":")[1].replace("\n","")
            experiment_parameters['lockIn2_unit']["r"] = param_file_list[45].split(":")[1].replace("\n","")
            experiment_parameters['lockIn2_unit']["theta"] = param_file_list[46].split(":")[1].replace("\n","")
            
            experiment_parameters['fields_name']["field"] = param_file_list[49].split(":")[1].replace("\n","")
            experiment_parameters['fields_unit']["field"] = param_file_list[50].split(":")[1].replace("\n","")
            
            experiment_parameters['currents_name']["current"] = param_file_list[53].split(":")[1].replace("\n","")
            experiment_parameters['currents_unit']["current"] = param_file_list[54].split(":")[1].replace("\n","")
            
            experiment_parameters['times_name']["times"] = param_file_list[57].split(":")[1].replace("\n","")
            
        except FileNotFoundError:
            experiment_parameters = {'temperatures_name':{"ch_A":"Ch_A","ch_B":"Ch_B","ch_C":"Ch_C","ch_D":"Ch_D"}, 'temperatures_unit':{"ch_A":"K","ch_B":"K","ch_C":"K","ch_D":"K"},
                                    'resistances_name':{"ch_A":"Ch_A","ch_B":"Ch_B","ch_C":"Ch_C","ch_D":"Ch_D"}, 'resistances_unit':{"ch_A":"Ohms","ch_B":"Ohms","ch_C":"Ohms","ch_D":"Ohms"},
                                    'lockIn_name':{"x":"X","y":"Y","r":"R","theta":"Theta"}, 'lockIn_unit':{"x":"manual","y":"manual","r":"manual","theta":"degrees"},
                                    'lockIn2_name':{"x":"X","y":"Y","r":"R","theta":"Theta"}, 'lockIn2_unit':{"x":"manual","y":"manual","r":"manual","theta":"degrees"},
                                    'fields_name':{"field":"field"}, 'fields_unit':{"field":"T"},
                                    'currents_name':{"current":"current"}, 'currents_unit':{"current":"A"},
                                    'times_name':{"time":"time"}}
        
        channels_list = list(data.keys())[0:len(experiment_parameters[name_key].keys())]
        

        for ch in channels_list:
            combo_box.addItem(experiment_parameters[name_key][ch])

            
            
        return experiment_parameters
    
    def update_data(self, datasetLink, channel_list, comboBox, empty_set, axis, empty_experiment_parameters, full_experiment_parameters, name_key, unit_key):
        
        dataset = pd.read_csv(datasetLink, header=[0,1])
        AxisChannel = channel_list[comboBox.currentIndex()]
        AxisName = self.plotNameLineEdit.text() + "_" + comboBox.currentText()
        
        empty_set[AxisName] = dataset[axis][AxisChannel].to_list()

        empty_experiment_parameters[name_key][AxisName] = full_experiment_parameters[name_key][AxisChannel]
        print(empty_experiment_parameters[name_key])
        if axis == 'times':
            pass
        else:
            empty_experiment_parameters[unit_key][AxisName] = full_experiment_parameters[unit_key][AxisChannel]
            print(empty_experiment_parameters[unit_key])
        
        
        return AxisName
        
    

        
    