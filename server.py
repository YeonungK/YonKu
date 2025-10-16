import sys
import time
import os
import glob

from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget, QMessageBox
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, QTimer, Qt, QSize
from PyQt5.QtGui import QCloseEvent
from PyQt5 import uic

from GUI import MagnetSupplyUi as ms, ChsBigLineUi as chs, GasValveUi as gv, PressureGaugeUi as pg, NewPlotSettingUi as nps, OpenPlotSettingUi as ops, PlotUi, TempControlUi as tc, ExperimentUi as eu, LockInAmplifier as li
from GUI import SerialInstCreateUi as sic, GpibInstCreateUi as gic, EthernetInstCreateUi as eic, USB6525InstCreateUi as bic
from GUI import DeviceListUi as dlu, SerialInstDeviceUi as sidu, GpibInstDeviceUi as gidu, EthernetInstDeviceUi as eidu, USB6525InstDeviceUi as uidu
from Tools import LakeShore_336, INFICON_VGC401, GasValve, SRS_830, Oxford_MercuryiPS, DataLogger, Dataset, NewQMdiSubWindow

from datetime import datetime
from zoneinfo import ZoneInfo

class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        
        
        
        uic.loadUi("GUI/ui_files/graphene.ui", self)
        
        self.mdi = self.mdiArea_2
        self.mdi_plot = self.mdiArea
        
        self.tempWid = tc.tempControlUi()
        self.experimentWid = eu.ExperimentUi()
        self.gasWid = gv.GasUi()
        self.lockInWid = li.LockInAmpUi()
        self.pressureWid = pg.PressureUi()
        self.magnetSupplyWid = ms.MagnetPowerUi()
        
        self.add_windows()
        
        self.showMaximized()
        self.show()

    
    def add_windows(self): 
        
        self.gasSub = NewQMdiSubWindow.NewQMdiSubWindow(self.actionGas_Valve)
        self.lockInSub = NewQMdiSubWindow.NewQMdiSubWindow(self.actionLock_In_Amplifier)
        self.magnetSupplySub = NewQMdiSubWindow.NewQMdiSubWindow(self.actionMagnet_Power_Supply)
        self.tempSub = NewQMdiSubWindow.NewQMdiSubWindow(self.actionTemperature_Controller)
        self.pressureSub = NewQMdiSubWindow.NewQMdiSubWindow(self.actionPressure_Gauge)
        self.experimentSub = NewQMdiSubWindow.NewQMdiSubWindow(self.actionExperiment)
        
        
        self.gasSub.setWidget(self.gasWid)
        self.lockInSub.setWidget(self.lockInWid)
        self.magnetSupplySub.setWidget(self.magnetSupplyWid)
        self.tempSub.setWidget(self.tempWid)
        self.pressureSub.setWidget(self.pressureWid)
        self.experimentSub.setWidget(self.experimentWid)
        
        
        self.gasSub.setWindowTitle("gas_valve")
        self.lockInSub.setWindowTitle("lock_in_amplifier")
        self.magnetSupplySub.setWindowTitle("magnet_power_supply")
        self.tempSub.setWindowTitle("temperature_controller")
        self.pressureSub.setWindowTitle("pressure_gauge")
        self.experimentSub.setWindowTitle("experiment")
        
        self.gasSub.resize(100,100)
        self.lockInSub.resize(100, 100)
        self.magnetSupplySub.resize(100, 100)
        self.tempSub.resize(100,100)
        self.pressureSub.resize(100,100)
        self.experimentSub.resize(100, 100)
        
        self.mdi.addSubWindow(self.gasSub)
        self.mdi.addSubWindow(self.lockInSub)
        self.mdi.addSubWindow(self.magnetSupplySub)
        self.mdi.addSubWindow(self.tempSub)
        self.mdi.addSubWindow(self.pressureSub)
        self.mdi.addSubWindow(self.experimentSub)
        
        self.gasSub.move(0, 0)
        self.lockInSub.move(0, 0)
        self.magnetSupplySub.move(0, 0)
        self.tempSub.move(0, 0)
        self.pressureSub.move(0,0)
        self.experimentSub.move(0,0)
        
        self.gasSub.show()
        self.lockInSub.show()
        self.magnetSupplySub.show()
        self.tempSub.show()
        self.pressureSub.show()
        self.experimentSub.hide()
        
        # self.mdi.tileSubWindows()
        
        self.chA_line_sub = chs.chABigLineUi()
        # self.chA_line_sub.move(100,100)
        self.chA_line_sub.hide()
        
        self.chB_line_sub = chs.chBBigLineUi()
        # self.chB_line_sub.move(100,100)
        self.chB_line_sub.hide()
        
        self.chC_line_sub = chs.chCBigLineUi()
        # self.chC_line_sub.move(100,100)
        self.chC_line_sub.hide()
        
        self.chD_line_sub = chs.chDBigLineUi()
        # self.chD_line_sub.move(100,100)
        self.chD_line_sub.hide()
        
        # device list sub
        self.deviceListSub = dlu.DeviceListUi(self.mdi)
    
        self.deviceListSub.hide()
        
if __name__ == "__main__":
    
    
    app = QApplication(sys.argv)
    UIWindow = UI()
    app.exec()