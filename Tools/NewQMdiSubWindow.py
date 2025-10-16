from PyQt5.QtWidgets import QMdiSubWindow
from PyQt5.QtGui import QCloseEvent

class NewQMdiSubWindow(QMdiSubWindow):
    def __init__(self, device_button):
        super().__init__()
        
        self.device_button = device_button
            
    def closeEvent(self, event:QCloseEvent):
        self.hide()
        
    def hide(self):
        super().hide()
        self.device_button.setChecked(False)