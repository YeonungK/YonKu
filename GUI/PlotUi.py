import sys

sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')

import numpy as np
import h5py
import time
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox, QCheckBox, QMdiSubWindow
from PyQt5.QtGui import QIcon, QCloseEvent
from PyQt5.QtCore import QTimer, Qt, QSize
import pyqtgraph as pg
import pandas as pd

from GUI import AddMultidataPlotUi as amp



class plotWidget(QWidget):
    def __init__(self, plot_setting, dataset, experiment_parameters):
        super().__init__()
        
        # [PlotItem Related Variables (Dataset, Plot setting, Axes type, etc.)]

        # data dictionaries
        self.temperature = dataset['temperature']
        self.resistance = dataset['resistance']
        self.lockIn = dataset['lockIn']
        self.lockIn2 = dataset['lockIn2']
        self.field = dataset['field']
        self.current = dataset['current']
        self.time = dataset['time']
        
        self.dataset = dataset
        self.experiment_parameters = experiment_parameters
        
        # plots
        self.plots = {}
        self.plot_count = 0
        
        # plot setting values
        self.xAxis = plot_setting[0]
        self.yAxis = plot_setting[1]
        self.xAxisHiLim = plot_setting[2]
        self.xAxisLoLim = plot_setting[3]
        self.yAxisHiLim = plot_setting[4]
        self.yAxisLoLim = plot_setting[5]
        self.ticVal = plot_setting[6]
        self.gridLine = plot_setting[7]
        self.symbol = plot_setting[8]
        self.experimentSettingWid = plot_setting[9]
        
        # Date axes initiation (required with pyqt date-and-time object)
        self.x_date_axis = pg.DateAxisItem(orientation='bottom',
                                        utcOffset=14400,               # set to your timezone offset if desired
                                        showValues=True,
                                        autoScale=True)
        self.y_date_axis = pg.DateAxisItem(orientation='left',
                                        utcOffset=14400,               # set to your timezone offset if desired
                                        showValues=True,
                                        autoScale=True)
        
        # plot title and trace colours
        self.title = self.yAxis.upper() + " vs " + self.xAxis.upper()
        self.colors = ['r', 'g', 'y', 'c', 'w']
        
        # set the xAxis and yAxis data type according to the exp setting ui & dataset
        match self.xAxis:
            case "lockIn":
                self.xAxisData = self.lockIn
                self.xAxis_name_key = 'lockIn_name'
                self.xAxis_unit_key = 'lockIn_unit'
            case "lockIn2":
                self.xAxisData = self.lockIn2
                self.xAxis_name_key = 'lockIn2_name'
                self.xAxis_unit_key = 'lockIn2_unit'
            case "temperature":
                self.xAxisData = self.temperature
                self.xAxis_name_key = 'temperature_name'
                self.xAxis_unit_key = 'temperature_unit'
            case "resistance":
                self.xAxisData = self.resistance
                self.xAxis_name_key = 'resistance_name'
                self.xAxis_unit_key = 'resistance_unit'
            case "field":
                self.xAxisData = self.field
                self.xAxis_name_key = 'field_name'
                self.xAxis_unit_key = 'field_unit'
            case "current":
                self.xAxisData = self.current
                self.xAxis_name_key = 'current_name'
                self.xAxis_unit_key = 'current_unit'
            case "time":
                self.xAxisData = self.time
                self.xAxis_name_key = 'time_name'
        match self.yAxis:
            case "lockIn":
                self.yAxisData = self.lockIn
                self.yAxis_name_key = 'lockIn_name'
                self.yAxis_unit_key = 'lockIn_unit'
            case "lockIn2":
                self.yAxisData = self.lockIn2
                self.yAxis_name_key = 'lockIn2_name'
                self.yAxis_unit_key = 'lockIn2_unit'
            case "temperature":
                self.yAxisData = self.temperature
                self.yAxis_name_key = 'temperature_name'
                self.yAxis_unit_key = 'temperature_unit'
            case "resistance":
                self.yAxisData = self.resistance
                self.yAxis_name_key = 'resistance_name'
                self.yAxis_unit_key = 'resistance_unit'
            case "field":
                self.yAxisData = self.field
                self.yAxis_name_key = 'field_name'
                self.yAxis_unit_key = 'field_unit'
            case "current":
                self.yAxisData = self.current
                self.yAxis_name_key = 'current_name'
                self.yAxis_unit_key = 'current_unit'
            case "time":
                self.yAxisData = self.time
                self.yAxis_name_key = 'time_name'
         # [/]
        
        # [Plot Window Related Variables (layouts, comboboxes, buttons)]

        # x axis stuff
        self.xAxisLabel = QLabel("x-Axis")
        self.xAxisLabel.setAlignment(Qt.AlignCenter)
        
        self.xAxisUnitLabel = QLabel(self.xAxis.upper())
        self.xAxisUnitLabel.setAlignment(Qt.AlignCenter)
        
        self.xAxisUnitComboBox = self.create_combo_box('x')
        
        self.layout1 = QVBoxLayout()
        self.layout1.addWidget(self.xAxisLabel)
        self.layout1.addWidget(self.xAxisUnitLabel)
        self.layout1.addWidget(self.xAxisUnitComboBox)
        
        # y axis stuff
        self.yAxisLabel = QLabel("y-Axis")
        self.yAxisLabel.setAlignment(Qt.AlignCenter)
        
        self.yAxisUnitLabel = QLabel(self.yAxis.upper())
        self.yAxisUnitLabel.setAlignment(Qt.AlignCenter)
        
        self.yAxisUnitComboBox = self.create_combo_box('y')
        
        self.layout2 = QVBoxLayout()
        self.layout2.addWidget(self.yAxisLabel)
        self.layout2.addWidget(self.yAxisUnitLabel)
        self.layout2.addWidget(self.yAxisUnitComboBox)
        
        # New Plot button
        self.settingB = QPushButton()
        self.settingB.setText("Setting")
        self.newPlotB = QPushButton()
        self.newPlotB.setText("Add a new trace")

        self.layout3 = QVBoxLayout()
        self.layout3.addWidget(self.settingB)
        self.layout3.addWidget(self.newPlotB)
        
        # Wrapping layout
        self.layout4 = QHBoxLayout()
        self.layout4.addLayout(self.layout1)
        self.layout4.addLayout(self.layout2)
        self.layout4.addLayout(self.layout3)
        
        self.layout = QVBoxLayout() # [/]
        
        # [Created Plot Window]
        self.plot_widget = pg.PlotWidget()
        
        if self.xAxis == 'time':
            self.plot_widget.setAxisItems(axisItems = {'bottom': self.x_date_axis})
        if self.yAxis == 'time':
            self.plot_widget.setAxisItems(axisItems = {'left': self.y_date_axis})
        
        self.plot_widget.setTitle(self.title)
        self.plot_widget.addLegend(offset = [-1,20])
        self.layout.addLayout(self.layout4)
        self.layout.addWidget(self.plot_widget)
        self.setLayout(self.layout)
        
        # signals
        self.newPlotB.clicked.connect(self.create_new_plot)
         # [/]
   
    # [Functions]
    
    def create_new_plot(self): # trace == plot in this function
        
        # [Trace Info Extraction (channel, name, etc.)]

        # take the channel names of each Axis data type
        x_channel_list = list(self.xAxisData.keys())
        y_channel_list = list(self.yAxisData.keys())
        
        # choose the current channel from the combobox(we aren't using the combobox txt directly since they are not keys)
        xAxisChannel = x_channel_list[self.xAxisUnitComboBox.currentIndex()]
        yAxisChannel = y_channel_list[self.yAxisUnitComboBox.currentIndex()]
        
        # take the channel name from the experiment_parameters
        xAxisChannel_name = self.experiment_parameters[self.xAxis_name_key][xAxisChannel]
        yAxisChannel_name = self.experiment_parameters[self.yAxis_name_key][yAxisChannel]
        
        # Editing the time unit (non-existent)
        if not self.xAxis == 'time':
            xAxisChannel_unit = self.experiment_parameters[self.xAxis_unit_key][xAxisChannel]
        else:
            xAxisChannel_unit = "-"
        if not self.yAxis == 'time':    
            yAxisChannel_unit = self.experiment_parameters[self.yAxis_unit_key][yAxisChannel]
        else:
            yAxisChannel_unit = "-"
        
        # plot and channel names
        plot_name = yAxisChannel_name + " (" + yAxisChannel_unit + ")" + " vs " + xAxisChannel_name + " (" + xAxisChannel_unit + ")"
        plot_channels = yAxisChannel + " vs " + xAxisChannel # [/]
            
        # create a new trace with the extracted trace info
        if not plot_channels in self.plots:
            # data = np.array([self.xAxisData[xAxisChannel],self.yAxisData[yAxisChannel]], dtype=float)
            # data = data.transpose()
            self.plots[plot_channels] = self.plot_widget.plot(self.xAxisData[xAxisChannel], 
                                                                self.yAxisData[yAxisChannel], name = plot_name, pen = self.colors[self.plot_count % 5])
            self.plot_count += 1
        else:
            pass
        
        #print(self.plots.keys())
    
    def create_combo_box(self, Axis):
        
        combo_box = QComboBox()
        match Axis:
            case 'x':
                for ch in self.xAxisData.keys():
                    combo_box.addItem(self.experiment_parameters[self.xAxis_name_key][ch])
            case 'y':
                for ch in self.yAxisData.keys():
                    combo_box.addItem(self.experiment_parameters[self.yAxis_name_key][ch])
        
        return combo_box
    
    def plot_data(self): # update data for each plot
        
        for plt_channels, plts in self.plots.items():
            plt_channels = plt_channels.split(" vs ")
            print(plt_channels)
            # data = np.array([self.xAxisData[plt_channels[1]],self.yAxisData[plt_channels[0]]], dtype=float)
            # data = data.transpose()
            # plts.setData(data)
            plts.setData(self.xAxisData[plt_channels[1]],self.yAxisData[plt_channels[0]])

    def closeEvent(self, event:QCloseEvent):
        self.plots.clear()
        event.accept()
         # [/]


class oldPlotWidget(QWidget):
    def __init__(self, plot_setting):
        super().__init__()
        
        # [PlotItem Related Variables (plot setting, title, axes, dataset, experiment parameters)]

        # plots
        self.plots = {}
        self.plot_count = 0
        
        # plot setting values
        self.xAxis = plot_setting[0]
        self.yAxis = plot_setting[1]
        self.xAxisHiLim = plot_setting[2]
        self.xAxisLoLim = plot_setting[3]
        self.yAxisHiLim = plot_setting[4]
        self.yAxisLoLim = plot_setting[5]
        self.ticVal = plot_setting[6]
        self.gridLine = plot_setting[7]
        self.multipleDataset = plot_setting[9]
        self.experimentParamLink = plot_setting[10]
        self.experimentParamJson = plot_setting[11]
        

        # used for multiple time axes
        self.axes = {}
        self.axes_count = 1
        
        self.x_date_axis = pg.DateAxisItem(orientation='bottom',
                                        utcOffset=14400,               # set to your timezone offset if desired
                                        showValues=True,
                                        autoScale=True)
        self.y_date_axis = pg.DateAxisItem(orientation='left',
                                        utcOffset=14400,               # set to your timezone offset if desired
                                        showValues=True,
                                        autoScale=True)
        
        self.title = self.yAxis.upper() + " vs " + self.xAxis.upper()
        self.colors = ['w', 'r', 'g', 'y', 'c']
        
        
        # [Dataset Construction]

        # if it's a normal old plot
        if not self.multipleDataset:
            self.datasetLink = plot_setting[8]
            self.dataset = pd.read_csv(self.datasetLink, header=[0,1])
            self.set = {}

            for data_type, channel in self.dataset.columns:
                if data_type not in self.set:
                    self.set[data_type] = {}

                self.set[data_type][channel] = self.dataset[(data_type, channel)].to_list()

            # also expose each data_type as an attribute because the rest of your class uses self.temperature, self.lockIn, etc.
            for data_type, data_dict in self.set.items():
                setattr(self, data_type, data_dict)

            
            # for instrument in self.connected_instruments:
            #     for data_type, channel in self.all_instruments[instrument].data_type.items():
            #         self.data_dict = setattr(self, data_type, {})
            #         self.data_dict = getattr(self, data_type)
            #         for ch in channel:
            #             self.data_dict[ch] = self.dataset[data_type][ch].to_list()
                    
            #         self.set[data_type] = self.data_dict
            
            # self.time = {'time':self.dataset['time']['time'].to_list()}
            # self.set['time'] = self.time
            
            print(self.set)
        
        # if multiple dataset option is chosen    
        else:
            self.temperature = {'ch_A':[],'ch_B':[],'ch_C':[],'ch_D':[]}
            self.resistance = {'ch_A':[],'ch_B':[],'ch_C':[],'ch_D':[]}
            self.lockIn = {'x':[],'y':[],'r':[],'theta':[]}
            self.lockIn2 = {'x':[],'y':[],'r':[],'theta':[]}
            self.field = {'field':[]}
            self.current = {'current':[]}
            self.time = {'time':[]}
            
            self.set = self.set = {'temperature':self.temperature, 'resistance':self.resistance, 'lockIn':self.lockIn, 'field': self.field, 'current':self.current, 'time':self.time}
             # [/]
        
        # [Experiment Parameters Construction]
        
        # if it's a normal old plot
        if not self.multipleDataset :
            try:
                
                self.experiment_parameters = {'temperature_name':{"ch_A":"","ch_B":"","ch_C":"","ch_D":""}, 'temperature_unit':{"ch_A":"","ch_B":"","ch_C":"","ch_D":""},
                                        'resistance_name':{"ch_A":"","ch_B":"","ch_C":"","ch_D":""}, 'resistance_unit':{"ch_A":"","ch_B":"","ch_C":"","ch_D":""},
                                        'lockIn_name':{"x":"","y":"","r":"","theta":""}, 'lockIn_unit':{"x":"","y":"","r":"","theta":""},
                                        'lockIn2_name':{"x":"","y":"","r":"","theta":""}, 'lockIn2_unit':{"x":"","y":"","r":"","theta":""},
                                        'field_name':{"field":""}, 'field_unit':{"field":""},
                                        'current_name':{"current":""}, 'current_unit':{"current":""},
                                        'time_name':{"time":""}}
                
                
                self.experiment_parameters['temperature_name']["ch_A"] = self.experimentParamJson["data_schema"]["temperature"]["ch_A"]["label"]
                self.experiment_parameters['temperature_name']["ch_B"] = self.experimentParamJson["data_schema"]["temperature"]["ch_B"]["label"]
                self.experiment_parameters['temperature_name']["ch_C"] = self.experimentParamJson["data_schema"]["temperature"]["ch_C"]["label"]
                self.experiment_parameters['temperature_name']["ch_D"] = self.experimentParamJson["data_schema"]["temperature"]["ch_D"]["label"]

                self.experiment_parameters['temperature_unit']["ch_A"] = self.experimentParamJson["data_schema"]["temperature"]["ch_A"]["unit"]
                self.experiment_parameters['temperature_unit']["ch_B"] = self.experimentParamJson["data_schema"]["temperature"]["ch_B"]["unit"]
                self.experiment_parameters['temperature_unit']["ch_C"] = self.experimentParamJson["data_schema"]["temperature"]["ch_C"]["unit"]
                self.experiment_parameters['temperature_unit']["ch_D"] = self.experimentParamJson["data_schema"]["temperature"]["ch_D"]["unit"]

                
                self.experiment_parameters['resistance_name']["ch_A"] = self.experimentParamJson["data_schema"]["resistance"]["ch_A"]["label"]
                self.experiment_parameters['resistance_name']["ch_B"] = self.experimentParamJson["data_schema"]["resistance"]["ch_B"]["label"]
                self.experiment_parameters['resistance_name']["ch_C"] = self.experimentParamJson["data_schema"]["resistance"]["ch_C"]["label"]
                self.experiment_parameters['resistance_name']["ch_D"] = self.experimentParamJson["data_schema"]["resistance"]["ch_D"]["label"]
                
                self.experiment_parameters['resistance_unit']["ch_A"] = self.experimentParamJson["data_schema"]["resistance"]["ch_A"]["unit"]
                self.experiment_parameters['resistance_unit']["ch_B"] = self.experimentParamJson["data_schema"]["resistance"]["ch_B"]["unit"]
                self.experiment_parameters['resistance_unit']["ch_C"] = self.experimentParamJson["data_schema"]["resistance"]["ch_C"]["unit"]
                self.experiment_parameters['resistance_unit']["ch_D"] = self.experimentParamJson["data_schema"]["resistance"]["ch_D"]["unit"]

                self.experiment_parameters['lockIn_name']["x"] = self.experimentParamJson["data_schema"]["lockIn"]["x"]["label"]
                self.experiment_parameters['lockIn_name']["y"] = self.experimentParamJson["data_schema"]["lockIn"]["y"]["label"]
                self.experiment_parameters['lockIn_name']["r"] = self.experimentParamJson["data_schema"]["lockIn"]["r"]["label"]
                self.experiment_parameters['lockIn_name']["theta"] = self.experimentParamJson["data_schema"]["lockIn"]["theta"]["label"]

                self.experiment_parameters['lockIn_unit']["x"] = self.experimentParamJson["data_schema"]["lockIn"]["x"]["unit"]
                self.experiment_parameters['lockIn_unit']["y"] = self.experimentParamJson["data_schema"]["lockIn"]["y"]["unit"]
                self.experiment_parameters['lockIn_unit']["r"] = self.experimentParamJson["data_schema"]["lockIn"]["r"]["unit"]
                self.experiment_parameters['lockIn_unit']["theta"] = self.experimentParamJson["data_schema"]["lockIn"]["theta"]["unit"]

                self.experiment_parameters['lockIn2_name']["x"] = self.experimentParamJson["data_schema"]["lockIn2"]["x"]["label"]
                self.experiment_parameters['lockIn2_name']["y"] = self.experimentParamJson["data_schema"]["lockIn2"]["y"]["label"]
                self.experiment_parameters['lockIn2_name']["r"] = self.experimentParamJson["data_schema"]["lockIn2"]["r"]["label"]
                self.experiment_parameters['lockIn2_name']["theta"] = self.experimentParamJson["data_schema"]["lockIn2"]["theta"]["label"]

                self.experiment_parameters['lockIn2_unit']["x"] = self.experimentParamJson["data_schema"]["lockIn2"]["x"]["unit"]
                self.experiment_parameters['lockIn2_unit']["y"] = self.experimentParamJson["data_schema"]["lockIn2"]["y"]["unit"]
                self.experiment_parameters['lockIn2_unit']["r"] = self.experimentParamJson["data_schema"]["lockIn2"]["r"]["unit"]
                self.experiment_parameters['lockIn2_unit']["theta"] = self.experimentParamJson["data_schema"]["lockIn2"]["theta"]["unit"]
                
                self.experiment_parameters['field_name']["field"] = self.experimentParamJson["data_schema"]["field"]["label"]
                self.experiment_parameters['field_unit']["field"] = self.experimentParamJson["data_schema"]["field"]["unit"]
                
                self.experiment_parameters['current_name']["current"] = self.experimentParamJson["data_schema"]["current"]["label"]
                self.experiment_parameters['current_unit']["current"] = self.experimentParamJson["data_schema"]["current"]["unit"]
                
                self.experiment_parameters['time_name']["time"] = self.experimentParamJson["data_schema"]["time"]["label"]
                
            except FileNotFoundError:
                self.experiment_parameters = {'temperature_name':{"ch_A":"Ch_A","ch_B":"Ch_B","ch_C":"Ch_C","ch_D":"Ch_D"}, 'temperature_unit':{"ch_A":"K","ch_B":"K","ch_C":"K","ch_D":"K"},
                                      'resistance_name':{"ch_A":"Ch_A","ch_B":"Ch_B","ch_C":"Ch_C","ch_D":"Ch_D"}, 'resistance_unit':{"ch_A":"Ohms","ch_B":"Ohms","ch_C":"Ohms","ch_D":"Ohms"},
                                      'lockIn_name':{"x":"X","y":"Y","r":"R","theta":"Theta"}, 'lockIn_unit':{"x":"manual","y":"manual","r":"manual","theta":"degrees"},
                                      'lockIn2_name':{"x":"X","y":"Y","r":"R","theta":"Theta"}, 'lockIn2_unit':{"x":"manual","y":"manual","r":"manual","theta":"degrees"},
                                      'field_name':{"field":"field"}, 'field_unit':{"field":"T"},
                                      'current_name':{"current":"current"}, 'current_unit':{"current":"A"},
                                      'time_name':{"time":"time"}}
        
        # if multiple dataset option is chosen, don't take any parameters yet        
        else:
            self.experiment_parameters = {'temperature_name':{"ch_A":"","ch_B":"","ch_C":"","ch_D":""}, 'temperature_unit':{"ch_A":"","ch_B":"","ch_C":"","ch_D":""},
                                        'resistance_name':{"ch_A":"","ch_B":"","ch_C":"","ch_D":""}, 'resistance_unit':{"ch_A":"","ch_B":"","ch_C":"","ch_D":""},
                                        'lockIn_name':{"x":"","y":"","r":"","theta":""}, 'lockIn_unit':{"x":"","y":"","r":"","theta":""},
                                        'lockIn2_name':{"x":"","y":"","r":"","theta":""}, 'lockIn2_unit':{"x":"","y":"","r":"","theta":""},
                                        'field_name':{"field":""}, 'field_unit':{"field":""},
                                        'current_name':{"current":""}, 'current_unit':{"current":""},
                                        'time_name':{"time":""}} # [/]
            
        # set the xAxis and yAxis data type according to the exp setting ui & dataset
        match self.xAxis:
            case "lockIn":
                self.xAxisData = self.lockIn
                self.x_set_name = 'lockIn'
                self.xAxis_name_key = 'lockIn_name'
                self.xAxis_unit_key = 'lockIn_unit'
            case "lockIn2":
                self.xAxisData = self.lockIn2
                self.x_set_name = 'lockIn2'
                self.xAxis_name_key = 'lockIn2_name'
                self.xAxis_unit_key = 'lockIn2_unit'
            case "temperature":
                self.xAxisData = self.temperature
                self.x_set_name = 'temperature'
                self.xAxis_name_key = 'temperature_name'
                self.xAxis_unit_key = 'temperature_unit'
            case "resistance":
                self.xAxisData = self.resistance
                self.x_set_name = 'resistance'
                self.xAxis_name_key = 'resistance_name'
                self.xAxis_unit_key = 'resistance_unit'
            case "field":
                self.xAxisData = self.field
                self.x_set_name = 'field'
                self.xAxis_name_key = 'field_name'
                self.xAxis_unit_key = 'field_unit'
            case "current":
                self.xAxisData = self.current
                self.x_set_name = 'current'
                self.xAxis_name_key = 'current_name'
                self.xAxis_unit_key = 'current_unit'
            case "time":
                self.xAxisData = self.time
                self.x_set_name = 'time'
                self.xAxis_name_key = 'time_name'
                self.xAxis_unit_key = 'time_unit' 
        match self.yAxis:
            case "lockIn":
                self.yAxisData = self.lockIn
                self.y_set_name = 'lockIn'
                self.yAxis_name_key = 'lockIn_name'
                self.yAxis_unit_key = 'lockIn_unit'
            case "lockIn2":
                self.yAxisData = self.lockIn2
                self.y_set_name = 'lockIn2'
                self.yAxis_name_key = 'lockIn2_name'
                self.yAxis_unit_key = 'lockIn2_unit'
            case "temperature":
                self.yAxisData = self.temperature
                self.y_set_name = 'temperature'
                self.yAxis_name_key = 'temperature_name'
                self.yAxis_unit_key = 'temperature_unit'
            case "resistance":
                self.yAxisData = self.resistance
                self.y_set_name = 'resistance'
                self.yAxis_name_key = 'resistance_name'
                self.yAxis_unit_key = 'resistance_unit'
            case "field":
                self.yAxisData = self.field
                self.y_set_name = 'field'
                self.yAxis_name_key = 'field_name'
                self.yAxis_unit_key = 'field_unit'
            case "current":
                self.yAxisData = self.current
                self.y_set_name = 'current'
                self.yAxis_name_key = 'current_name'
                self.yAxis_unit_key = 'current_unit'
            case "time":
                self.yAxisData = self.time
                self.y_set_name = 'time'
                self.yAxis_name_key = 'time_name'
                self.yAxis_unit_key = 'time_unit'
         # [/]
        
        # [Plot Window Related Variables (layouts, comboboxes, buttons)]

        # x axis stuff
        self.xAxisLabel = QLabel("x-Axis")
        self.xAxisLabel.setAlignment(Qt.AlignCenter)
        
        self.xAxisUnitLabel = QLabel(self.xAxis.upper())
        self.xAxisUnitLabel.setAlignment(Qt.AlignCenter)
        
        self.xAxisUnitComboBox = self.create_combo_box('x')
        
        self.layout1 = QVBoxLayout()
        self.layout1.addWidget(self.xAxisLabel)
        self.layout1.addWidget(self.xAxisUnitLabel) 
        self.layout1.addWidget(self.xAxisUnitComboBox)
        
        # y axis stuff
        self.yAxisLabel = QLabel("y-Axis")
        self.yAxisLabel.setAlignment(Qt.AlignCenter)
        
        self.yAxisUnitLabel = QLabel(self.yAxis.upper())
        self.yAxisUnitLabel.setAlignment(Qt.AlignCenter)
        
        self.yAxisUnitComboBox = self.create_combo_box('y')
        
        self.layout2 = QVBoxLayout()
        self.layout2.addWidget(self.yAxisLabel)
        self.layout2.addWidget(self.yAxisUnitLabel)
        self.layout2.addWidget(self.yAxisUnitComboBox)
        
        # buttons
        self.settingB = QPushButton()
        self.settingB.setText("Setting")
        self.newPlotB = QPushButton()
        self.newPlotB.setText("Add a new trace")
        
        self.layout3 = QVBoxLayout()
        self.layout3.addWidget(self.settingB)
        self.layout3.addWidget(self.newPlotB)
    
        # wrapping layouts
        self.layout4 = QHBoxLayout()
        self.layout4.addLayout(self.layout1)
        self.layout4.addLayout(self.layout2)
        self.layout4.addLayout(self.layout3)
        
        self.layout = QVBoxLayout() # [/]
        
        # [Plot Window Creation]

        # instantiate a graphicsview instead of a plot widget (for multiple axes)
        self.graphics_view = pg.GraphicsView()
        self.graphics_layout = pg.GraphicsLayout()
        self.graphics_view.setCentralWidget(self.graphics_layout)
        self.plot_item = pg.PlotItem()
        self.plot_legend = self.plot_item.addLegend(offset = [-1,20])
        self.graphics_layout.addItem(self.plot_item, row=1, col=1)
        
        # set time axes if needed
        if self.xAxis == 'time':
            self.plot_item.setAxisItems(axisItems = {'bottom': self.x_date_axis})
        if self.yAxis == 'time':
            self.plot_item.setAxisItems(axisItems = {'left': self.y_date_axis})
        
        # set the layout or whatever
        self.plot_item.setTitle(self.title)
        self.layout.addLayout(self.layout4)
        self.layout.addWidget(self.graphics_view)
        self.setLayout(self.layout)
        
        self.bottom_axis = self.plot_item.getAxis('bottom')
        self.left_axis = self.plot_item.getAxis('left')

        # Set labels for the axes
        self.bottom_axis.setLabel(text=self.xAxis)
        self.left_axis.setLabel(text=self.yAxis)
        
        # signals
        if not self.multipleDataset:
            self.newPlotB.clicked.connect(self.create_new_plot) # normal old plot
        else:
            self.newPlotB.clicked.connect(self.open_multidataset_plot) # multi dataset plot # [/] 
        
    # [Functions]
    
    # [Multi dataset functions]
    def open_multidataset_plot(self):
        
        self.amp_window = QMainWindow()
        self.addMultiDataPlotWid = amp.add_multidata_plot_ui(self.x_set_name, self.y_set_name, self.xAxis_name_key, self.yAxis_name_key,
                                                            self.xAxis_unit_key, self.yAxis_unit_key, self.xAxisData, self.yAxisData, self.experiment_parameters, self.all_instruments)

        self.amp_window.setCentralWidget(self.addMultiDataPlotWid)
        self.amp_window.setWindowTitle("Add a new trace")
        self.amp_window.resize(550, 213)
        self.addMultiDataPlotWid.xAxisLabel.setText(self.xAxis.upper())
        self.addMultiDataPlotWid.yAxisLabel.setText(self.yAxis.upper())
        self.amp_window.show()
        
        if self.xAxis == 'time' or self.yAxis == 'time' or self.xAxis == 'field' or self.yAxis == 'field':
            self.addMultiDataPlotWid.addPlotButton.clicked.connect(self.multidataset_update_all_multiaxes) # those data types need multiple axes
        else:
            self.addMultiDataPlotWid.addPlotButton.clicked.connect(self.multidataset_update_all) # the rest don't
         
    def multidataset_update_all_multiaxes(self):
        xAxisChannel_name = self.addMultiDataPlotWid.update_data(self.addMultiDataPlotWid.datasetLink, self.addMultiDataPlotWid.x_channel_list, self.addMultiDataPlotWid.xAxisChannelComboBox, 
                                             self.xAxisData, self.addMultiDataPlotWid.xAxis, self.experiment_parameters, self.addMultiDataPlotWid.expParam,
                                             self.addMultiDataPlotWid.xAxis_name_key, self.addMultiDataPlotWid.xAxis_unit_key)
        yAxisChannel_name = self.addMultiDataPlotWid.update_data(self.addMultiDataPlotWid.datasetLink, self.addMultiDataPlotWid.y_channel_list, self.addMultiDataPlotWid.yAxisChannelComboBox, 
                                             self.yAxisData, self.addMultiDataPlotWid.yAxis, self.experiment_parameters, self.addMultiDataPlotWid.expParam,
                                             self.addMultiDataPlotWid.yAxis_name_key, self.addMultiDataPlotWid.yAxis_unit_key)
        if xAxisChannel_name == None or yAxisChannel_name == None:
            return None
        
        
        self.amp_window.hide()
        
        self.secondary_viewboxes = []
        self.main_viewbox = self.plot_item.vb # get main viewbox
        self.previous_viewbox = None
        self.main_layout = self.plot_item.layout
        
        if not self.xAxis == 'time':
            xAxisChannel_unit = self.experiment_parameters[self.xAxis_unit_key][xAxisChannel_name]
        else:
            xAxisChannel_unit = "-"
            
        if not self.yAxis == 'time':    
            yAxisChannel_unit = self.experiment_parameters[self.yAxis_unit_key][yAxisChannel_name]
        else:
            yAxisChannel_unit = "-"
        
        plot_name = yAxisChannel_name + " (" + yAxisChannel_unit + ")" + " vs " + xAxisChannel_name + " (" + xAxisChannel_unit + ")"
        plot_channels = xAxisChannel_name + " vs " + yAxisChannel_name
        
        
        if self.plot_count == 0:
            main_x_axis = self.plot_item.getAxis("bottom")
            
            main_y_axis = self.plot_item.getAxis("left")
            
            self.main_viewbox.setMouseMode(pg.ViewBox.RectMode)
            
            self.main_layout.removeItem(main_y_axis) # remove items created in PlotItem from its layout
            self.main_layout.removeItem(main_x_axis)
            self.main_layout.removeItem(self.main_viewbox)

            self.main_layout.addItem(main_y_axis, 1, 0)  # shift them to the right, making space for secondary axes
            self.main_layout.addItem(self.main_viewbox, 1, 1)
            self.main_layout.addItem(main_x_axis,  2, 1)
                
            if self.xAxis == 'time' or self.xAxis == 'field':
                print("This is executing")
                main_x_axis.setLabel(xAxisChannel_name + " (" + xAxisChannel_unit + ")")
                self.main_layout.setRowStretchFactor(2, 0)
                
            print(self.yAxis)
            if self.yAxis == 'time' or self.yAxis == 'field':
                print("This is executing")
                main_y_axis.setLabel(yAxisChannel_name + " (" + yAxisChannel_unit + ")")
                self.main_layout.setRowStretchFactor(2, 0)
            
            viewbox = self.previous_viewbox = self.main_viewbox
                
            self.plots[plot_channels] = pg.PlotDataItem(self.xAxisData[xAxisChannel_name], 
                                                                self.yAxisData[yAxisChannel_name], name = plot_name, pen = self.colors[self.plot_count % 5])
            self.plot_legend.addItem(self.plots[plot_channels], self.plots[plot_channels].name())
                
            
            
        else:
            if self.xAxis == 'time' or self.xAxis == 'field':
                
                self.plots[plot_channels] = pg.PlotDataItem(self.xAxisData[xAxisChannel_name], 
                                                            self.yAxisData[yAxisChannel_name], name = plot_name, pen = self.colors[self.plot_count % 5])
                self.plot_legend.addItem(self.plots[plot_channels], self.plots[plot_channels].name())
                
                if self.xAxis == 'time':
                    self.axes[plot_channels] = pg.DateAxisItem(orientation='bottom',
                                                                utcOffset=14400,               # set to your timezone offset if desired
                                                                showValues=True,
                                                                autoScale=True)
                elif self.xAxis == 'field':
                    self.axes[plot_channels] = pg.AxisItem(orientation='bottom',
                                                                showValues=True,
                                                                autoScale=True)
                self.axes[plot_channels].setTextPen(self.colors[self.plot_count % 5])
                self.axes[plot_channels].setLabel(plot_name)
                self.main_layout.addItem(self.axes[plot_channels], 2+self.plot_count, 1)
                self.main_layout.setRowStretchFactor(2+self.plot_count, 2)
                
                viewbox = pg.ViewBox()  # create ViewBox
                viewbox.setYLink(self.main_viewbox)  # link to previous
                self.previous_viewbox = viewbox
                self.axes[plot_channels].linkToView(viewbox)  # link axis with viewbox
                self.graphics_layout.scene().addItem(viewbox)  # add viewbox to layout
                viewbox.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)  # autorange once to fit views at start

                self.secondary_viewboxes.append(viewbox)
            
            if self.yAxis == 'time' or self.yAxis == 'field':
                
                self.plots[plot_channels] = pg.PlotDataItem(self.xAxisData[xAxisChannel_name], 
                                                            self.yAxisData[yAxisChannel_name], name = plot_name, pen = self.colors[self.plot_count % 5])
                self.plot_legend.addItem(self.plots[plot_channels], self.plots[plot_channels].name())
                
                if self.yAxis == 'time':
                    self.axes[plot_channels] = pg.DateAxisItem(orientation='right',
                                                                utcOffset=14400,               # set to your timezone offset if desired
                                                                showValues=True,
                                                                autoScale=True)
                elif self.yAxis == 'field':
                    self.axes[plot_channels] = pg.AxisItem(orientation='right',
                                                                showValues=True,
                                                                autoScale=True)
                self.axes[plot_channels].setTextPen(self.colors[self.plot_count % 5])
                
                self.axes[plot_channels].setLabel(plot_name)
                self.main_layout.addItem(self.axes[plot_channels], 1, 1+self.plot_count)
                #self.main_layout.setColumnStretchFactor(-1, 2)
                
                viewbox = pg.ViewBox()  # create ViewBox
                viewbox.setXLink(self.main_viewbox)  # link to previous
                self.previous_viewbox = viewbox
                self.axes[plot_channels].linkToView(viewbox)  # link axis with viewbox
                self.graphics_layout.scene().addItem(viewbox)  # add viewbox to layout
                viewbox.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)  # autorange once to fit views at start

                self.secondary_viewboxes.append(viewbox)
                
                

        
        self.main_viewbox.sigResized.connect(self.updateViews)
        # self.updateViews()
        
        viewbox.addItem(self.plots[plot_channels])
        self.plot_count += 1
        
    def multidataset_update_all(self):
        
        xAxisChannel_name = self.addMultiDataPlotWid.update_data(self.addMultiDataPlotWid.datasetLink, self.addMultiDataPlotWid.x_channel_list, self.addMultiDataPlotWid.xAxisChannelComboBox, 
                                             self.xAxisData, self.addMultiDataPlotWid.xAxis, self.experiment_parameters, self.addMultiDataPlotWid.expParam,
                                             self.addMultiDataPlotWid.xAxis_name_key, self.addMultiDataPlotWid.xAxis_unit_key)
        yAxisChannel_name = self.addMultiDataPlotWid.update_data(self.addMultiDataPlotWid.datasetLink, self.addMultiDataPlotWid.y_channel_list, self.addMultiDataPlotWid.yAxisChannelComboBox, 
                                             self.yAxisData, self.addMultiDataPlotWid.yAxis, self.experiment_parameters, self.addMultiDataPlotWid.expParam,
                                             self.addMultiDataPlotWid.yAxis_name_key, self.addMultiDataPlotWid.yAxis_unit_key)

        self.amp_window.hide()
        
        
        if not self.xAxis == 'time':
            xAxisChannel_unit = self.experiment_parameters[self.xAxis_unit_key][xAxisChannel_name]
        else:
            xAxisChannel_unit = "-"
            
            
        if not self.yAxis == 'time':    
            yAxisChannel_unit = self.experiment_parameters[self.yAxis_unit_key][yAxisChannel_name]
        else:
            yAxisChannel_unit = "-"
        
        plot_name = yAxisChannel_name + " (" + yAxisChannel_unit + ")" + " vs " + xAxisChannel_name + " (" + xAxisChannel_unit + ")"
        plot_channels = xAxisChannel_name + " vs " + yAxisChannel_name
        
        if not plot_channels in self.plots:
            self.plots[plot_channels] = self.plot_item.plot(self.xAxisData[xAxisChannel_name], 
                                                                self.yAxisData[yAxisChannel_name], name = plot_name, pen = self.colors[self.plot_count % 5])
            

            self.plot_count += 1
        else:
            pass
    
    def updateViews(self):
        for vb in self.secondary_viewboxes:
            vb.setGeometry(self.main_viewbox.sceneBoundingRect())
        # [/]
    
    # [Single dataset functions]
    def create_new_plot(self):
        
        x_channel_list = list(self.xAxisData.keys())
        y_channel_list = list(self.yAxisData.keys())
        
        xAxisChannel = x_channel_list[self.xAxisUnitComboBox.currentIndex()]
        yAxisChannel = y_channel_list[self.yAxisUnitComboBox.currentIndex()]
        
        xAxisChannel_name = self.experiment_parameters[self.xAxis_name_key][xAxisChannel]
        yAxisChannel_name = self.experiment_parameters[self.yAxis_name_key][yAxisChannel]
        
        if not self.xAxis == 'time':
            xAxisChannel_unit = self.experiment_parameters[self.xAxis_unit_key][xAxisChannel]
        else:
            xAxisChannel_unit = "-"
             
        if not self.yAxis == 'time':    
            yAxisChannel_unit = self.experiment_parameters[self.yAxis_unit_key][yAxisChannel]
        else:
            yAxisChannel_unit = "-"
        
        plot_name = yAxisChannel_name + " (" + yAxisChannel_unit + ")" + " vs " + xAxisChannel_name + " (" + xAxisChannel_unit + ")"
        plot_channels = yAxisChannel + " vs " + xAxisChannel
    
        if not plot_channels in self.plots:
            self.plots[plot_channels] = self.plot_item.plot(self.xAxisData[xAxisChannel], 
                                                                self.yAxisData[yAxisChannel], name = plot_name, pen = self.colors[self.plot_count % 5])

            self.plot_count += 1
        else:
            pass
        
        #print(self.plots.keys())
     
    def create_combo_box(self, Axis):
        
        combo_box = QComboBox()
        
        if not self.multipleDataset:
            match Axis:
                case 'x':
                    for ch in self.xAxisData.keys():
                        combo_box.addItem(self.experiment_parameters[self.xAxis_name_key][ch])
                case 'y':
                    for ch in self.yAxisData.keys():
                        combo_box.addItem(self.experiment_parameters[self.yAxis_name_key][ch])
        else:
            combo_box.setEnabled(False)
        
        return combo_box
 # [/]
 # [/]
        
