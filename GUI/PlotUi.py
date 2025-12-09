import sys

sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')

import numpy as np
import h5py
import time
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox, QCheckBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, Qt, QSize
import pyqtgraph as pg
import pandas as pd

from GUI import ShowHidePlotUi as shp, AddMultidataPlotUi as amp



class plotWidget(QWidget):
    def __init__(self, plot_setting, dataset, experiment_parameters):
        super().__init__()
        
        # measurements
        self.temperature = dataset['temperature']
        self.resistance = dataset['resistance']
        self.lockIn = dataset['lockIn']
        self.lockIn2 = dataset['lockIn2']
        self.field = dataset['field']
        self.current = dataset['current']
        self.time = dataset['time']
        
        self.dataset = dataset
        
        self.experiment_parameters = experiment_parameters
        
        # # show/hide plot ui
        # self.showHidePlotUi = shp.ShowHidePlotUi()
        
        # self.showlabel = QLabel("Show")
        # self.showlabel.setAlignment(Qt.AlignTop)
        
        # self.layout0 = QVBoxLayout()
        # self.layout0.addWidget(self.showlabel)
        
        # self.showHidePlotUi.setLayout(self.layout0)
        
        # self.plotCheckBoxes = {}
        
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
        
        self.x_date_axis = pg.DateAxisItem(orientation='bottom',
                                        utcOffset=14400,               # set to your timezone offset if desired
                                        showValues=True,
                                        autoScale=True)
        
        self.y_date_axis = pg.DateAxisItem(orientation='left',
                                        utcOffset=14400,               # set to your timezone offset if desired
                                        showValues=True,
                                        autoScale=True)
        
        self.title = self.yAxis.upper() + " vs " + self.xAxis.upper()
        
        self.colors = ['r', 'g', 'y', 'c', 'w']
        
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
        
        """create plot widget"""
        
        # labels and buttons
        
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
        # self.showHideB = QPushButton()
        # self.showHideB.setText("Show/Hide plots")
        
        # self.showHideB.clicked.connect(self.showHidePlotUi_show)
        
        self.layout3 = QVBoxLayout()
        self.layout3.addWidget(self.settingB)
        self.layout3.addWidget(self.newPlotB)
        # self.layout3.addWidget(self.showHideB)
        
        # more layouts
        self.layout4 = QHBoxLayout()
        self.layout4.addLayout(self.layout1)
        self.layout4.addLayout(self.layout2)
        self.layout4.addLayout(self.layout3)
        
        self.layout = QVBoxLayout()
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
        
        
        # create plots
        # self.plot = self.plot_widget.plot(pen=pg.mkPen(color='r', width=2), name='CH1')
        
        # # set buffer size and create data dict
        # self.buffer_size = 60 * 60 * 7
        # self.data = {'CH1': {'x': [], 'y': []}}
        
        # # make a data logger
        # self.logger = dt.MultiChannelLogger("multichannel_log.h5", 'CH1')
       
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
            
        # self.plots[plot_channels] = self.plot_widget.plot(self.xAxisData[xAxisChannel], 
        #                                                     self.yAxisData[yAxisChannel])
        
        if not plot_channels in self.plots:
            self.plots[plot_channels] = self.plot_widget.plot(self.xAxisData[xAxisChannel], 
                                                                self.yAxisData[yAxisChannel], name = plot_name, pen = self.colors[self.plot_count % 5])

            # self.plotCheckBoxes[plot_channels] = self.create_check_box(plot_channels, self.colors[self.plot_count % 5], self.plots[plot_channels])
            # self.layout0.addWidget(self.plotCheckBoxes[plot_channels])
            
            self.plot_count += 1
        else:
            pass
        
        
        
        print(self.plots.keys())
     
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
    
    # def showHidePlotUi_show(self):
    #     self.showHidePlotUi.show()

        
    
    # def create_check_box(self, text, colour, plot):
        
    #     check_box = QCheckBox(text)
    #     # check_box.setIcon(QIcon(f'{colour}_icon.png'))
    #     # check_box.setIconSize(QSize(24,24))
        
    #     check_box.setChecked(True)
    #     # check_box.stateChanged.connect(self.show_hide_plot)
        
        
    #     return check_box

    # def show_hide_plot(self, signal_arg, key):
    #     # if self.plotCheckBoxes[key].isChecked():
    #     #     self.plots[key].show()
    #     # else:
    #     #     self.plots[key].hide()
    #     pass
        
        

    def plot_data(self):

        # if len(self.data['CH1']['x']) > self.buffer_size:
        #         self.data['CH1']['x'] = self.data['CH1']['x'][-self.buffer_size:]
        #         self.data['CH1']['y'] = self.data['CH1']['y'][-self.buffer_size:]
                
        # self.plot.setData(self.data['CH1']['x'], self.data['CH1']['y'])
        
        
        for plt_channels, plts in self.plots.items():
            
            plt_channels = plt_channels.split(" vs ")
            print(plt_channels)
            plts.setData(self.xAxisData[plt_channels[1]],self.yAxisData[plt_channels[0]])
        
        # self.logger.append(now, new_value)
        pass
        


class oldPlotWidget(QWidget):
    def __init__(self, plot_setting, instruments):
        super().__init__()
        
        
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
        self.connected_instruments = plot_setting[11]
        self.all_instruments = instruments
        
        print(self.connected_instruments, self.all_instruments)

        
        # used for multiple time axes
        self.axes = {}
        self.axes_count = 1
        
        # dataset
        
        if not self.multipleDataset:
            self.datasetLink = plot_setting[8]
            self.dataset = pd.read_csv(self.datasetLink, header=[0,1])
            self.set = {}
            
            for instrument in self.connected_instruments:
                for data_type, channel in self.all_instruments[instrument].data_type.items():
                    self.data_dict = setattr(self, data_type, {})
                    self.data_dict = getattr(self, data_type)
                    for ch in channel:
                        self.data_dict[ch] = self.dataset[data_type][ch].to_list()
                    
                    self.set[data_type] = self.data_dict
            
            self.time = {'time':self.dataset['time']['time'].to_list()}
            self.set['time'] = self.time
            
            print(self.set)
            
        else:
            self.temperature = {'ch_A':[],'ch_B':[],'ch_C':[],'ch_D':[]}
            self.resistance = {'ch_A':[],'ch_B':[],'ch_C':[],'ch_D':[]}
            self.lockIn = {'x':[],'y':[],'r':[],'theta':[]}
            self.lockIn2 = {'x':[],'y':[],'r':[],'theta':[]}
            self.field = {'field':[]}
            self.current = {'current':[]}
            self.time = {'time':[]}
            
            self.set = self.set = {'temperature':self.temperature, 'resistance':self.resistance, 'lockIn':self.lockIn, 'field': self.field, 'current':self.current, 'time':self.time}
            
        # experiment_parameters
        
        if not self.multipleDataset :
            try:
                self.param_file = open(self.experimentParamLink)
                
                self.param_file_list = self.param_file.readlines()
                
                self.experiment_parameters = {'temperature_name':{"ch_A":"","ch_B":"","ch_C":"","ch_D":""}, 'temperature_unit':{"ch_A":"","ch_B":"","ch_C":"","ch_D":""},
                                        'resistance_name':{"ch_A":"","ch_B":"","ch_C":"","ch_D":""}, 'resistance_unit':{"ch_A":"","ch_B":"","ch_C":"","ch_D":""},
                                        'lockIn_name':{"x":"","y":"","r":"","theta":""}, 'lockIn_unit':{"x":"","y":"","r":"","theta":""},
                                        'lockIn2_name':{"x":"","y":"","r":"","theta":""}, 'lockIn2_unit':{"x":"","y":"","r":"","theta":""},
                                        'field_name':{"field":""}, 'field_unit':{"field":""},
                                        'current_name':{"current":""}, 'current_unit':{"current":""},
                                        'time_name':{"time":""}}
                
                print(self.param_file_list)
                
                self.experiment_parameters['temperature_name']["ch_A"] = self.param_file_list[5].split(":")[1].replace("\n","")
                self.experiment_parameters['temperature_name']["ch_B"] = self.param_file_list[6].split(":")[1].replace("\n","")
                self.experiment_parameters['temperature_name']["ch_C"] = self.param_file_list[7].split(":")[1].replace("\n","")
                self.experiment_parameters['temperature_name']["ch_D"] = self.param_file_list[8].split(":")[1].replace("\n","")
                
                self.experiment_parameters['temperature_unit']["ch_A"] = self.param_file_list[10].split(":")[1].replace("\n","")
                self.experiment_parameters['temperature_unit']["ch_B"] = self.param_file_list[11].split(":")[1].replace("\n","")
                self.experiment_parameters['temperature_unit']["ch_C"] = self.param_file_list[12].split(":")[1].replace("\n","")
                self.experiment_parameters['temperature_unit']["ch_D"] = self.param_file_list[13].split(":")[1].replace("\n","")
                
                self.experiment_parameters['resistance_name']["ch_A"] = self.param_file_list[16].split(":")[1].replace("\n","")
                self.experiment_parameters['resistance_name']["ch_B"] = self.param_file_list[17].split(":")[1].replace("\n","")
                self.experiment_parameters['resistance_name']["ch_C"] = self.param_file_list[18].split(":")[1].replace("\n","")
                self.experiment_parameters['resistance_name']["ch_D"] = self.param_file_list[19].split(":")[1].replace("\n","")
                
                self.experiment_parameters['resistance_unit']["ch_A"] = self.param_file_list[21].split(":")[1].replace("\n","")
                self.experiment_parameters['resistance_unit']["ch_B"] = self.param_file_list[22].split(":")[1].replace("\n","")
                self.experiment_parameters['resistance_unit']["ch_C"] = self.param_file_list[23].split(":")[1].replace("\n","")
                self.experiment_parameters['resistance_unit']["ch_D"] = self.param_file_list[24].split(":")[1].replace("\n","")

                self.experiment_parameters['lockIn_name']["x"] = self.param_file_list[27].split(":")[1].replace("\n","")
                self.experiment_parameters['lockIn_name']["y"] = self.param_file_list[28].split(":")[1].replace("\n","")
                self.experiment_parameters['lockIn_name']["r"] = self.param_file_list[29].split(":")[1].replace("\n","")
                self.experiment_parameters['lockIn_name']["theta"] = self.param_file_list[30].split(":")[1].replace("\n","")
                
                self.experiment_parameters['lockIn_unit']["x"] = self.param_file_list[32].split(":")[1].replace("\n","")
                self.experiment_parameters['lockIn_unit']["y"] = self.param_file_list[33].split(":")[1].replace("\n","")
                self.experiment_parameters['lockIn_unit']["r"] = self.param_file_list[34].split(":")[1].replace("\n","")
                self.experiment_parameters['lockIn_unit']["theta"] = self.param_file_list[35].split(":")[1].replace("\n","")
                
                self.experiment_parameters['lockIn2_name']["x"] = self.param_file_list[38].split(":")[1].replace("\n","")
                self.experiment_parameters['lockIn2_name']["y"] = self.param_file_list[39].split(":")[1].replace("\n","")
                self.experiment_parameters['lockIn2_name']["r"] = self.param_file_list[40].split(":")[1].replace("\n","")
                self.experiment_parameters['lockIn2_name']["theta"] = self.param_file_list[41].split(":")[1].replace("\n","")
                
                self.experiment_parameters['lockIn2_unit']["x"] = self.param_file_list[43].split(":")[1].replace("\n","")
                self.experiment_parameters['lockIn2_unit']["y"] = self.param_file_list[44].split(":")[1].replace("\n","")
                self.experiment_parameters['lockIn2_unit']["r"] = self.param_file_list[45].split(":")[1].replace("\n","")
                self.experiment_parameters['lockIn2_unit']["theta"] = self.param_file_list[46].split(":")[1].replace("\n","")
                
                self.experiment_parameters['field_name']["field"] = self.param_file_list[49].split(":")[1].replace("\n","")
                self.experiment_parameters['field_unit']["field"] = self.param_file_list[50].split(":")[1].replace("\n","")
                
                self.experiment_parameters['current_name']["current"] = self.param_file_list[53].split(":")[1].replace("\n","")
                self.experiment_parameters['current_unit']["current"] = self.param_file_list[54].split(":")[1].replace("\n","")
                
                self.experiment_parameters['time_name']["time"] = self.param_file_list[57].split(":")[1].replace("\n","")
                
            except FileNotFoundError:
                self.experiment_parameters = {'temperature_name':{"ch_A":"Ch_A","ch_B":"Ch_B","ch_C":"Ch_C","ch_D":"Ch_D"}, 'temperature_unit':{"ch_A":"K","ch_B":"K","ch_C":"K","ch_D":"K"},
                                      'resistance_name':{"ch_A":"Ch_A","ch_B":"Ch_B","ch_C":"Ch_C","ch_D":"Ch_D"}, 'resistance_unit':{"ch_A":"Ohms","ch_B":"Ohms","ch_C":"Ohms","ch_D":"Ohms"},
                                      'lockIn_name':{"x":"X","y":"Y","r":"R","theta":"Theta"}, 'lockIn_unit':{"x":"manual","y":"manual","r":"manual","theta":"degrees"},
                                      'lockIn2_name':{"x":"X","y":"Y","r":"R","theta":"Theta"}, 'lockIn2_unit':{"x":"manual","y":"manual","r":"manual","theta":"degrees"},
                                      'field_name':{"field":"field"}, 'field_unit':{"field":"T"},
                                      'current_name':{"current":"current"}, 'current_unit':{"current":"A"},
                                      'time_name':{"time":"time"}}
                
        else:
            self.experiment_parameters = {'temperature_name':{"ch_A":"","ch_B":"","ch_C":"","ch_D":""}, 'temperature_unit':{"ch_A":"","ch_B":"","ch_C":"","ch_D":""},
                                        'resistance_name':{"ch_A":"","ch_B":"","ch_C":"","ch_D":""}, 'resistance_unit':{"ch_A":"","ch_B":"","ch_C":"","ch_D":""},
                                        'lockIn_name':{"x":"","y":"","r":"","theta":""}, 'lockIn_unit':{"x":"","y":"","r":"","theta":""},
                                        'lockIn2_name':{"x":"","y":"","r":"","theta":""}, 'lockIn2_unit':{"x":"","y":"","r":"","theta":""},
                                        'field_name':{"field":""}, 'field_unit':{"field":""},
                                        'current_name':{"current":""}, 'current_unit':{"current":""},
                                        'time_name':{"time":""}}
            

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
        
        """create plot widget"""
        
        # labels and buttons
        
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
        

        # more layouts
        self.layout4 = QHBoxLayout()
        self.layout4.addLayout(self.layout1)
        self.layout4.addLayout(self.layout2)
        self.layout4.addLayout(self.layout3)
        
        self.layout = QVBoxLayout()
        
        self.graphics_view = pg.GraphicsView()
        self.graphics_layout = pg.GraphicsLayout()
        self.graphics_view.setCentralWidget(self.graphics_layout)
        self.plot_item = pg.PlotItem()
        self.plot_legend = self.plot_item.addLegend(offset = [-1,20])
        self.graphics_layout.addItem(self.plot_item, row=1, col=1)
        

        if self.xAxis == 'time':
            self.plot_item.setAxisItems(axisItems = {'bottom': self.x_date_axis})
        if self.yAxis == 'time':
            self.plot_item.setAxisItems(axisItems = {'left': self.y_date_axis})
        
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
            self.newPlotB.clicked.connect(self.create_new_plot)
        else:
            self.newPlotB.clicked.connect(self.open_multidataset_plot)
        
        
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
            self.addMultiDataPlotWid.addPlotButton.clicked.connect(self.multidataset_update_all_multiaxes)
            
        else:
            self.addMultiDataPlotWid.addPlotButton.clicked.connect(self.multidataset_update_all)
            
            
            
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
        self.updateViews()
        
        viewbox.addItem(self.plots[plot_channels])
        self.plot_count += 1
        
    def updateViews(self):
        for vb in self.secondary_viewboxes:
            vb.setGeometry(self.main_viewbox.sceneBoundingRect())

            
    def multidataset_update_all(self):
        
        xAxisChannel_name = self.addMultiDataPlotWid.update_data(self.addMultiDataPlotWid.datasetLink, self.addMultiDataPlotWid.x_channel_list, self.addMultiDataPlotWid.xAxisChannelComboBox, 
                                             self.xAxisData, self.addMultiDataPlotWid.xAxis, self.experiment_parameters, self.addMultiDataPlotWid.expParam,
                                             self.addMultiDataPlotWid.xAxis_name_key, self.addMultiDataPlotWid.xAxis_unit_key)
        yAxisChannel_name = self.addMultiDataPlotWid.update_data(self.addMultiDataPlotWid.datasetLink, self.addMultiDataPlotWid.y_channel_list, self.addMultiDataPlotWid.yAxisChannelComboBox, 
                                             self.yAxisData, self.addMultiDataPlotWid.yAxis, self.experiment_parameters, self.addMultiDataPlotWid.expParam,
                                             self.addMultiDataPlotWid.yAxis_name_key, self.addMultiDataPlotWid.yAxis_unit_key)
        #self.name_count += self.addMultiDataPlotWid.internal_count
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
        
        
        # self.plots[plot_channels] = self.plot_widget.plot(self.xAxisData[xAxisChannel], 
        #                                                     self.yAxisData[yAxisChannel])
        

        if not plot_channels in self.plots:
            self.plots[plot_channels] = self.plot_item.plot(self.xAxisData[xAxisChannel_name], 
                                                                self.yAxisData[yAxisChannel_name], name = plot_name, pen = self.colors[self.plot_count % 5])
            

            self.plot_count += 1
        else:
            pass
       
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
        
        
        # self.plots[plot_channels] = self.plot_widget.plot(self.xAxisData[xAxisChannel], 
        #                                                     self.yAxisData[yAxisChannel])
        

        if not plot_channels in self.plots:
            self.plots[plot_channels] = self.plot_item.plot(self.xAxisData[xAxisChannel], 
                                                                self.yAxisData[yAxisChannel], name = plot_name, pen = self.colors[self.plot_count % 5])

            self.plot_count += 1
        else:
            pass
        print(self.plots.keys())
        
    
    def showHidePlotUi_show(self):
        self.showHidePlotUi.show()
        
         
    def create_check_box(self, text, colour, plot):
        
        check_box = QCheckBox(text)
        # check_box.setIcon(QIcon(f'{colour}_icon.png'))
        # check_box.setIconSize(QSize(24,24))
        
        check_box.setChecked(True)
        check_box.stateChanged.connect(self.show_hide_plot)
        
        
        return check_box

    def show_hide_plot(self):
        for key, plot in self.plots.items():
            if self.plotCheckBoxes[key].isChecked():
                plot.show()
            else:
                plot.hide()
     
     
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

        
    
