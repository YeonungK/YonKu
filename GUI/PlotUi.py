import sys



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
        

        self.xAxisData = self.dataset.get(self.xAxis, {})
        self.yAxisData = self.dataset.get(self.yAxis, {})

        if not self.xAxisData:
            print(f"Warning: x-axis data type '{self.xAxis}' not found in dataset.")

        if not self.yAxisData:
            print(f"Warning: y-axis data type '{self.yAxis}' not found in dataset.")

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
    
    def get_schema_entry(self, data_type, channel):
        schema = self.experiment_parameters.get("data_schema", {})

        key = f"{data_type}_{channel}"


        return schema.get(key, {
            "label": channel,
            "unit": "-"
        })

    def get_label(self, data_type, channel):
        return self.get_schema_entry(data_type, channel).get("label", channel)


    def get_unit(self, data_type, channel):
        return self.get_schema_entry(data_type, channel).get("unit", "-")

    def create_new_plot(self): # trace == plot in this function
        
        # [Trace Info Extraction (channel, name, etc.)]

        # take the channel names of each Axis data type
        x_channel_list = list(self.xAxisData.keys())
        y_channel_list = list(self.yAxisData.keys())

        if not x_channel_list or not y_channel_list:
            print("No channels available for selected data types.")
            return
        
        # choose the current channel from the combobox(we aren't using the combobox txt directly since they are not keys)
        x_channel = x_channel_list[self.xAxisUnitComboBox.currentIndex()]
        y_channel = y_channel_list[self.yAxisUnitComboBox.currentIndex()]

        x_label = self.get_label(self.xAxis, x_channel)
        y_label = self.get_label(self.yAxis, y_channel)

        x_unit = self.get_unit(self.xAxis, x_channel)
        y_unit = self.get_unit(self.yAxis, y_channel)
        
        
        # plot and channel names
        plot_name = f"{y_label} ({y_unit}) vs {x_label} ({x_unit})"
        plot_key = f"{y_channel} vs {x_channel}" # [/]
            
        # create a new trace with the extracted trace info
        if not plot_key in self.plots:
            self.plots[plot_key] = self.plot_widget.plot(
                self.xAxisData[x_channel],
                self.yAxisData[y_channel],
                name=plot_name,
                pen=self.colors[self.plot_count % len(self.colors)]
            )
            self.plot_count += 1
        else:
            pass
        
    
    def create_combo_box(self, axis):
        combo_box = QComboBox()

        if axis == "x":
            for channel in self.xAxisData.keys():
                combo_box.addItem(self.get_label(self.xAxis, channel))

        elif axis == "y":
            for channel in self.yAxisData.keys():
                combo_box.addItem(self.get_label(self.yAxis, channel))

        return combo_box
    
    def plot_data(self): # update data for each plot
        
        for plt_channels, plts in self.plots.items():
            plt_channels = plt_channels.split(" vs ")
            print(plt_channels)
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
                self.set.setdefault(data_type, {})
                self.set[data_type][channel] = self.dataset[(data_type, channel)].to_list()


            self.xAxisData = self.set.get(self.xAxis, {})
            self.yAxisData = self.set.get(self.yAxis, {})

            
        
        # if multiple dataset option is chosen    
        else:
            
            self.set = {}
            self.xAxisData = {}
            self.yAxisData = {}

            
            # [/]
        
        # [Experiment Parameters Construction]
        
        # if it's a normal old plot
        if not self.multipleDataset :
            
            self.experiment_parameters = self.experimentParamJson
                
        
        # if multiple dataset option is chosen, don't take any parameters yet        
        else:
            self.experiment_parameters = {} # [/]
            
        # set the xAxis and yAxis data type according to the exp setting ui & dataset
        self.xAxisData = self.set.get(self.xAxis, {})
        self.x_set_name = self.xAxis
        self.xAxis_name_key = f'{self.x_set_name}_name'
        self.xAxis_unit_key = f'{self.x_set_name}__unit'
        self.yAxisData = self.set.get(self.yAxis, {})
        self.y_set_name = self.yAxis
        self.yAxis_name_key = f'{self.y_set_name}_name'
        self.yAxis_unit_key = f'{self.y_set_name}__unit'

       
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

        if not self.multipleDataset:
            self.plot_widget = pg.PlotWidget()
            self.plot_item = self.plot_widget.getPlotItem()

            self.plot_legend = self.plot_item.addLegend(offset=[-1, 20])

            # set time axes if needed
            if self.xAxis == 'time':
                self.plot_item.setAxisItems(axisItems = {'bottom': self.x_date_axis})
            if self.yAxis == 'time':
                self.plot_item.setAxisItems(axisItems = {'left': self.y_date_axis})
            
            # set the layout or whatever
            self.plot_item.setTitle(self.title)
            self.layout.addLayout(self.layout4)
            self.layout.addWidget(self.plot_widget)
            self.setLayout(self.layout)
            
            self.bottom_axis = self.plot_item.getAxis('bottom')
            self.left_axis = self.plot_item.getAxis('left')

            # Set labels for the axes
            self.bottom_axis.setLabel(text=self.xAxis)
            self.left_axis.setLabel(text=self.yAxis)
        
        else: # if it is multidataset

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
    
    def get_schema_entry(self, data_type, channel):
        schema = self.experiment_parameters.get("data_schema", {})
        key = f"{data_type}_{channel}"

        return schema.get(key, {
            "label": channel,
            "unit": "-"
        })


    def get_label(self, data_type, channel):
        return self.get_schema_entry(data_type, channel).get("label", channel)


    def get_unit(self, data_type, channel):
        return self.get_schema_entry(data_type, channel).get("unit", "-")

    # [Multi dataset functions]
    def open_multidataset_plot(self):
        
        self.amp_window = QMainWindow()
        self.addMultiDataPlotWid = amp.add_multidata_plot_ui(self.x_set_name, self.y_set_name, self.xAxis_name_key, self.yAxis_name_key,
                                                            self.xAxis_unit_key, self.yAxis_unit_key, self.xAxisData, self.yAxisData, self.experiment_parameters)

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
        if self.addMultiDataPlotWid.AxisDatasetLineEdit.text() == "" or self.addMultiDataPlotWid.AxisDatasetLineEdit.text() == "This dataset doesn't include the chosen data types.":
            self.addMultiDataPlotWid.AxisDatasetLineEdit.setText("Please choose a dataset.")
        else:
            xAxisChannel_name, xAxisChannel_unit = self.addMultiDataPlotWid.update_data(self.addMultiDataPlotWid.datasetLink, self.addMultiDataPlotWid.x_channel_list, self.addMultiDataPlotWid.xAxisChannelComboBox, 
                                                self.xAxisData, self.addMultiDataPlotWid.xAxis, self.experiment_parameters, self.addMultiDataPlotWid.expParam,
                                                self.addMultiDataPlotWid.xAxis_name_key, self.addMultiDataPlotWid.xAxis_unit_key)
            yAxisChannel_name, yAxisChannel_unit = self.addMultiDataPlotWid.update_data(self.addMultiDataPlotWid.datasetLink, self.addMultiDataPlotWid.y_channel_list, self.addMultiDataPlotWid.yAxisChannelComboBox, 
                                                self.yAxisData, self.addMultiDataPlotWid.yAxis, self.experiment_parameters, self.addMultiDataPlotWid.expParam,
                                                self.addMultiDataPlotWid.yAxis_name_key, self.addMultiDataPlotWid.yAxis_unit_key)
            if xAxisChannel_name == None or yAxisChannel_name == None:
                return None
            
            
            self.amp_window.hide()
            
            self.secondary_viewboxes = []
            self.main_viewbox = self.plot_item.vb # get main viewbox
            self.previous_viewbox = None
            self.main_layout = self.plot_item.layout
            
            
            plot_name = f"{yAxisChannel_name} ({yAxisChannel_unit}) vs {xAxisChannel_name} ({xAxisChannel_unit})"
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
                    main_x_axis.setLabel(plot_name)
                    self.main_layout.setRowStretchFactor(2, 0)
                    
                print(self.yAxis)
                if self.yAxis == 'time' or self.yAxis == 'field':
                    print("This is executing")
                    main_y_axis.setLabel(plot_name)
                    self.main_layout.setRowStretchFactor(2, 0)
                
                viewbox = self.previous_viewbox = self.main_viewbox
                    
                self.plots[plot_channels] = pg.PlotDataItem(self.xAxisData[xAxisChannel_name], 
                                                                    self.yAxisData[yAxisChannel_name], name = plot_name, pen = self.colors[self.plot_count % 5])
                self.plot_legend.addItem(self.plots[plot_channels], self.plots[plot_channels].name())
                    
                
                
            else:
                x_special = self.xAxis in ["time", "field"]
                y_special = self.yAxis in ["time", "field"]

                x_data = self.xAxisData[xAxisChannel_name]
                y_data = self.yAxisData[yAxisChannel_name]

                # Create ONE plot item and ONE legend entry
                self.plots[plot_channels] = pg.PlotDataItem(
                    x_data,
                    y_data,
                    name=plot_name,
                    pen=self.colors[self.plot_count % 5]
                )

                self.plot_legend.addItem(
                    self.plots[plot_channels],
                    self.plots[plot_channels].name()
                )

                # Create ONE viewbox for this trace
                viewbox = pg.ViewBox()
                self.graphics_layout.scene().addItem(viewbox)

                # Link only the shared/non-special axis
                if x_special and not y_special:
                    viewbox.setYLink(self.main_viewbox)

                if y_special and not x_special:
                    viewbox.setXLink(self.main_viewbox)

                # Create extra x-axis if needed
                if x_special:
                    if self.xAxis == "time":
                        x_axis = pg.DateAxisItem(
                            orientation="bottom",
                            utcOffset=14400,
                            showValues=True,
                            autoScale=True
                        )
                    else:
                        x_axis = pg.AxisItem(
                            orientation="bottom",
                            showValues=True,
                            autoScale=True
                        )

                    x_axis.setTextPen(self.colors[self.plot_count % 5])
                    x_axis.setLabel(plot_name)
                    x_axis.linkToView(viewbox)

                    self.axes[f"{plot_channels}_x"] = x_axis
                    self.main_layout.addItem(x_axis, 2 + self.plot_count, 1)
                    self.main_layout.setRowStretchFactor(2 + self.plot_count, 2)

                # Create extra y-axis if needed
                if y_special:
                    if self.yAxis == "time":
                        y_axis = pg.DateAxisItem(
                            orientation="right",
                            utcOffset=14400,
                            showValues=True,
                            autoScale=True
                        )
                    else:
                        y_axis = pg.AxisItem(
                            orientation="right",
                            showValues=True,
                            autoScale=True
                        )

                    y_axis.setTextPen(self.colors[self.plot_count % 5])
                    y_axis.setLabel(plot_name)
                    y_axis.linkToView(viewbox)

                    self.axes[f"{plot_channels}_y"] = y_axis
                    self.main_layout.addItem(y_axis, 1, 1 + self.plot_count)

                # Add plot to the viewbox
                viewbox.addItem(self.plots[plot_channels])

                # Autoscale using ALL plotted data so far
                all_x = []
                all_y = []

                for plot in self.plots.values():
                    xs, ys = plot.getData()

                    if xs is not None and len(xs) > 0:
                        all_x.extend(xs)

                    if ys is not None and len(ys) > 0:
                        all_y.extend(ys)

                if x_special and not y_special:
                    if all_y:
                        self.main_viewbox.setYRange(min(all_y), max(all_y), padding=0.05)

                elif y_special and not x_special:
                    if all_x:
                        self.main_viewbox.setXRange(min(all_x), max(all_x), padding=0.05)

                elif x_special and y_special:
                    if all_x:
                        viewbox.setXRange(min(all_x), max(all_x), padding=0.05)

                    if all_y:
                        viewbox.setYRange(min(all_y), max(all_y), padding=0.05)

                viewbox.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=False)

                self.secondary_viewboxes.append(viewbox)
                    
                    
                    

                
                    
                    
                    
                    

                    
                    

            
            self.main_viewbox.sigResized.connect(self.updateViews)
            
            viewbox.addItem(self.plots[plot_channels])
            self.plot_count += 1
        
    def multidataset_update_all(self):

        if self.addMultiDataPlotWid.AxisDatasetLineEdit.text() == "" or self.addMultiDataPlotWid.AxisDatasetLineEdit.text() == "This dataset doesn't include the chosen data types.":
            self.addMultiDataPlotWid.AxisDatasetLineEdit.setText("Please choose a dataset.")
        else:
        
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

                # [Trace Info Extraction (channel, name, etc.)]

        # take the channel names of each Axis data type
        x_channel_list = list(self.xAxisData.keys())
        y_channel_list = list(self.yAxisData.keys())

        if not x_channel_list or not y_channel_list:
            print("No channels available for selected data types.")
            return
        
        # choose the current channel from the combobox(we aren't using the combobox txt directly since they are not keys)
        x_channel = x_channel_list[self.xAxisUnitComboBox.currentIndex()]
        y_channel = y_channel_list[self.yAxisUnitComboBox.currentIndex()]

        x_label = self.get_label(self.xAxis, x_channel)
        y_label = self.get_label(self.yAxis, y_channel)

        x_unit = self.get_unit(self.xAxis, x_channel)
        y_unit = self.get_unit(self.yAxis, y_channel)
        
        
        # plot and channel names
        plot_name = f"{y_label} ({y_unit}) vs {x_label} ({x_unit})"
        plot_key = f"{y_channel} vs {x_channel}" # [/]
            
        # create a new trace with the extracted trace info
        if not plot_key in self.plots:
            self.plots[plot_key] = self.plot_widget.plot(
                self.xAxisData[x_channel],
                self.yAxisData[y_channel],
                name=plot_name,
                pen=self.colors[self.plot_count % len(self.colors)]
            )
            self.plot_count += 1
        else:
            pass
        
        
     
    def create_combo_box(self, axis):
        
        combo_box = QComboBox()

        if axis == "x":
            for channel in self.xAxisData.keys():
                combo_box.addItem(self.get_label(self.xAxis, channel))

        elif axis == "y":
            for channel in self.yAxisData.keys():
                combo_box.addItem(self.get_label(self.yAxis, channel))

        return combo_box
 # [/]
 # [/]
        
