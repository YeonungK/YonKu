import sys

sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')

from GUI.instrument_control_widgets import widget

class test_instrument_widget(widget.widget):
    def __init__(self, instrument):
        super().__init__(instrument, 'GUI/ui_files/instrument_control_uis/test_model_ui.ui')
        
