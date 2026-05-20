

from project_paths import PROJECT_ROOT

from GUI.instrument_control_widgets import base_dynamic_widget

class test_serial_two_widget(base_dynamic_widget.widget):
    def __init__(self, instrument, device_info, device_key, parent):
        
        super().__init__(instrument, device_info, device_key, parent, 'GUI/ui_files/instrument_control_uis/test_serial_two_model_ui.ui')
        
    def initialize_widget(self):
        pass