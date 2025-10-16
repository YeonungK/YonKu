import sys
import numpy as np
import h5py
import time
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
from Tools import LakeShore_336 as tc
import pyvisa


class temp_plot(QWidget):
    def __init__(self):
        super().__init__()
        
        # self.instrument = tc.temperatureController('temperature_controller', 'COM4')
        
        # create plot widget
        self.layout = QVBoxLayout()
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setTitle("Temperature vs Time")
        self.layout.addWidget(self.plot_widget)
        self.setLayout(self.layout)
        
        # create plot
        self.plot = self.plot_widget.plot(pen=pg.mkPen(color='r', width=2), name='CH1')
        
        # set buffer size and create data dict
        self.buffer_size = 60 * 60 * 7
        self.data = {'CH1': {'x': [], 'y': []}}
        
        
        
    
    def start(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)  # 1Hz
        print("plot started")
    
    def update(self):
        # now = datetime.now().timestamp()
        # new_value = self.instrument.temp_read('A')
        
        # self.data['CH1']['x'].append(now)
        # self.data['CH1']['y'].append(new_value)

        # if len(self.data['CH1']['x']) > self.buffer_size:
        #         self.data['CH1']['x'] = self.data['CH1']['x'][-self.buffer_size:]
        #         self.data['CH1']['y'] = self.data['CH1']['y'][-self.buffer_size:]
                
        # self.plot.setData(self.data['CH1']['x'], self.data['CH1']['y'])
        
        # self.logger.append(now, new_value)
        pass
        
    def stop(self):
        self.timer.stop()

        