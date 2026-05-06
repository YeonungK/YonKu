import sys

from project_paths import GUI_DIR

from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMdiSubWindow, QMdiArea, QPushButton, QTextEdit, QWidget
from PyQt5 import uic


        


class ExperimentSettingUi(QWidget):
    def __init__(self):
        super().__init__()

        uic.loadUi(f"{GUI_DIR}/ui_files/experiment_setting.ui", self)
        
        self.dataComboBox.currentIndexChanged.connect(self.data_type_switch)
        self.saveButton.clicked.connect(self.save_button)
        
        # Default values
        self.temperature_ch_A_name = "Ch_A"
        self.temperature_ch_B_name = "Ch_B"
        self.temperature_ch_C_name = "Ch_C"
        self.temperature_ch_D_name = "Ch_D"
        
        self.temperature_ch_A_unit = "K"
        self.temperature_ch_B_unit = "K"
        self.temperature_ch_C_unit = "K"
        self.temperature_ch_D_unit = "K"
        
        
        self.resistance_ch_A_name = "Ch_A"
        self.resistance_ch_B_name = "Ch_B"
        self.resistance_ch_C_name = "Ch_C"
        self.resistance_ch_D_name = "Ch_D"
        
        self.resistance_ch_A_unit = "Ohms"
        self.resistance_ch_B_unit = "Ohms"
        self.resistance_ch_C_unit = "Ohms"
        self.resistance_ch_D_unit = "Ohms"
        
        
        self.lockIn_x_name = "X"
        self.lockIn_y_name = "Y"
        self.lockIn_r_name = "R"
        self.lockIn_theta_name = "Theta"
        
        self.lockIn_x_unit = "manual"
        self.lockIn_y_unit = "manual"
        self.lockIn_r_unit = "manual"
        self.lockIn_theta_unit = "degrees"
        
        
        self.lockIn2_x_name = "X"
        self.lockIn2_y_name = "Y"
        self.lockIn2_r_name = "R"
        self.lockIn2_theta_name = "Theta"
        
        self.lockIn2_x_unit = "manual"
        self.lockIn2_y_unit = "manual"
        self.lockIn2_r_unit = "manual"
        self.lockIn2_theta_unit = "degrees"
        
        self.field_name = "Field"
        
        self.field_unit = "T"
        
        self.current_name = "Current"
        
        self.current_unit = "A"
        
        self.time_name = "Time"
        
        self.experiment_parameters_ui = {'temperature_name':{"ch_A":"","ch_B":"","ch_C":"","ch_D":""}, 'temperature_unit':{"ch_A":"","ch_B":"","ch_C":"","ch_D":""},
                                      'resistance_name':{"ch_A":"","ch_B":"","ch_C":"","ch_D":""}, 'resistance_unit':{"ch_A":"","ch_B":"","ch_C":"","ch_D":""},
                                      'lockIn_name':{"x":"","y":"","r":"","theta":""}, 'lockIn_unit':{"x":"","y":"","r":"","theta":""},
                                      'lockIn2_name':{"x":"","y":"","r":"","theta":""}, 'lockIn2_unit':{"x":"","y":"","r":"","theta":""},
                                      'field_name':{"field":""}, 'field_unit':{"field":""},
                                      'current_name':{"current":""}, 'current_unit':{"current":""},
                                      'time_name':{"time":""}}

        self.experiment_parameters = {'temperature_name':{"ch_A":"Ch_A","ch_B":"Ch_B","ch_C":"Ch_C","ch_D":"Ch_D"}, 'temperature_unit':{"ch_A":"K","ch_B":"K","ch_C":"K","ch_D":"K"},
                                      'resistance_name':{"ch_A":"Ch_A","ch_B":"Ch_B","ch_C":"Ch_C","ch_D":"Ch_D"}, 'resistance_unit':{"ch_A":"Ohms","ch_B":"Ohms","ch_C":"Ohms","ch_D":"Ohms"},
                                      'lockIn_name':{"x":"X","y":"Y","r":"R","theta":"Theta"}, 'lockIn_unit':{"x":"manual","y":"manual","r":"manual","theta":"degrees"},
                                      'lockIn2_name':{"x":"X","y":"Y","r":"R","theta":"Theta"}, 'lockIn2_unit':{"x":"manual","y":"manual","r":"manual","theta":"degrees"},
                                      'field_name':{"field":"field"}, 'field_unit':{"field":"T"},
                                      'current_name':{"current":"current"}, 'current_unit':{"current":"A"},
                                      'time_name':{"time":"time"}}
    
    
    def save_button(self):
        self.update_values()
        self.save_all_values()
            
    def save_all_values(self):
        
        for key, list in self.experiment_parameters_ui.items():
            for channel, value in list.items():
                if not value == "":
                    self.experiment_parameters[key][channel] = value
                else:
                    pass
    
    
    def data_type_switch(self):
        
        self.show_channels()
        self.clear_lineEdit()
        self.change_lineEdit() 

    def show_channels(self):
        match self.dataComboBox.currentIndex():
            case 0:
                self.channel_1_label.setText("Ch_A:")
                self.channel_2_label.setText("Ch_B:")
                self.channel_3_label.setText("Ch_C:")
                self.channel_4_label.setText("Ch_D:")
                
                self.channel_2_label.setEnabled(True)
                self.channel_3_label.setEnabled(True)
                self.channel_4_label.setEnabled(True)
                
                self.channel_2_name.setEnabled(True)
                self.channel_3_name.setEnabled(True)
                self.channel_4_name.setEnabled(True)
                
                self.unit_2_label.setEnabled(True)
                self.unit_3_label.setEnabled(True)
                self.unit_4_label.setEnabled(True)
                
                self.channel_1_unit.setEnabled(True)
                self.channel_2_unit.setEnabled(True)
                self.channel_3_unit.setEnabled(True)
                self.channel_4_unit.setEnabled(True)
                
                self.channel_1_unit.setPlaceholderText("K")
                self.channel_2_unit.setPlaceholderText("K")
                self.channel_3_unit.setPlaceholderText("K")
                self.channel_4_unit.setPlaceholderText("K")
                
                
            case 1:
                self.channel_1_label.setText("Ch_A:")
                self.channel_2_label.setText("Ch_B:")
                self.channel_3_label.setText("Ch_C:")
                self.channel_4_label.setText("Ch_D:")
                
                self.channel_2_label.setEnabled(True)
                self.channel_3_label.setEnabled(True)
                self.channel_4_label.setEnabled(True)
                
                self.channel_2_name.setEnabled(True)
                self.channel_3_name.setEnabled(True)
                self.channel_4_name.setEnabled(True)
                
                self.unit_2_label.setEnabled(True)
                self.unit_3_label.setEnabled(True)
                self.unit_4_label.setEnabled(True)
                
                self.channel_1_unit.setEnabled(True)
                self.channel_2_unit.setEnabled(True)
                self.channel_3_unit.setEnabled(True)
                self.channel_4_unit.setEnabled(True)
                
                self.channel_1_unit.setPlaceholderText("Ohms")
                self.channel_2_unit.setPlaceholderText("Ohms")
                self.channel_3_unit.setPlaceholderText("Ohms")
                self.channel_4_unit.setPlaceholderText("Ohms")
                
            case 2:
                self.channel_1_label.setText("X:")
                self.channel_2_label.setText("Y:")
                self.channel_3_label.setText("R:")
                self.channel_4_label.setText("Theta:")
                
                self.channel_2_label.setEnabled(True)
                self.channel_3_label.setEnabled(True)
                self.channel_4_label.setEnabled(True)
                
                self.channel_2_name.setEnabled(True)
                self.channel_3_name.setEnabled(True)
                self.channel_4_name.setEnabled(True)
                
                self.unit_2_label.setEnabled(True)
                self.unit_3_label.setEnabled(True)
                self.unit_4_label.setEnabled(True)
                
                self.channel_1_unit.setEnabled(True)
                self.channel_2_unit.setEnabled(True)
                self.channel_3_unit.setEnabled(True)
                self.channel_4_unit.setEnabled(True)
                
                self.channel_1_unit.setPlaceholderText("manual")
                self.channel_2_unit.setPlaceholderText("manual")
                self.channel_3_unit.setPlaceholderText("manual")
                self.channel_4_unit.setPlaceholderText("degrees")
            
            case 3:
                self.channel_1_label.setText("X:")
                self.channel_2_label.setText("Y:")
                self.channel_3_label.setText("R:")
                self.channel_4_label.setText("Theta:")
                
                self.channel_2_label.setEnabled(True)
                self.channel_3_label.setEnabled(True)
                self.channel_4_label.setEnabled(True)
                
                self.channel_2_name.setEnabled(True)
                self.channel_3_name.setEnabled(True)
                self.channel_4_name.setEnabled(True)
                
                self.unit_2_label.setEnabled(True)
                self.unit_3_label.setEnabled(True)
                self.unit_4_label.setEnabled(True)
                
                self.channel_1_unit.setEnabled(True)
                self.channel_2_unit.setEnabled(True)
                self.channel_3_unit.setEnabled(True)
                self.channel_4_unit.setEnabled(True)
                
                self.channel_1_unit.setPlaceholderText("manual")
                self.channel_2_unit.setPlaceholderText("manual")
                self.channel_3_unit.setPlaceholderText("manual")
                self.channel_4_unit.setPlaceholderText("degrees")
                
            case 4:
                self.channel_1_label.setText("Field:")
                self.channel_2_label.setText("Channel:")
                self.channel_3_label.setText("Channel:")
                self.channel_4_label.setText("Channel:")
                self.channel_2_label.setEnabled(False)
                self.channel_3_label.setEnabled(False)
                self.channel_4_label.setEnabled(False)
                
                self.channel_2_name.setEnabled(False)
                self.channel_3_name.setEnabled(False)
                self.channel_4_name.setEnabled(False)
                
                self.unit_2_label.setEnabled(False)
                self.unit_3_label.setEnabled(False)
                self.unit_4_label.setEnabled(False)
                
                self.channel_1_unit.setEnabled(True)
                self.channel_2_unit.setEnabled(False)
                self.channel_3_unit.setEnabled(False)
                self.channel_4_unit.setEnabled(False)
                
                self.channel_1_unit.setPlaceholderText("T")
                self.channel_2_unit.setPlaceholderText("")
                self.channel_3_unit.setPlaceholderText("")
                self.channel_4_unit.setPlaceholderText("")
                
            case 5:
                self.channel_1_label.setText("Current:")
                self.channel_2_label.setText("Channel:")
                self.channel_3_label.setText("Channel:")
                self.channel_4_label.setText("Channel:")
                self.channel_2_label.setEnabled(False)
                self.channel_3_label.setEnabled(False)
                self.channel_4_label.setEnabled(False)
                
                self.channel_2_name.setEnabled(False)
                self.channel_3_name.setEnabled(False)
                self.channel_4_name.setEnabled(False)
                
                self.unit_2_label.setEnabled(False)
                self.unit_3_label.setEnabled(False)
                self.unit_4_label.setEnabled(False)
                
                self.channel_1_unit.setEnabled(True)
                self.channel_2_unit.setEnabled(False)
                self.channel_3_unit.setEnabled(False)
                self.channel_4_unit.setEnabled(False)
                
                self.channel_1_unit.setPlaceholderText("A")
                self.channel_2_unit.setPlaceholderText("")
                self.channel_3_unit.setPlaceholderText("")
                self.channel_4_unit.setPlaceholderText("")
                
            case 6:
                self.channel_1_label.setText("Time:")
                self.channel_2_label.setText("Channel:")
                self.channel_3_label.setText("Channel:")
                self.channel_4_label.setText("Channel:")
                self.channel_2_label.setEnabled(False)
                self.channel_3_label.setEnabled(False)
                self.channel_4_label.setEnabled(False)
                
                self.channel_2_name.setEnabled(False)
                self.channel_3_name.setEnabled(False)
                self.channel_4_name.setEnabled(False)
                
                self.unit_2_label.setEnabled(False)
                self.unit_3_label.setEnabled(False)
                self.unit_4_label.setEnabled(False)
                
                self.channel_1_unit.setEnabled(False)
                self.channel_2_unit.setEnabled(False)
                self.channel_3_unit.setEnabled(False)
                self.channel_4_unit.setEnabled(False)
                
                self.channel_1_unit.setPlaceholderText("")
                self.channel_2_unit.setPlaceholderText("")
                self.channel_3_unit.setPlaceholderText("")
                self.channel_4_unit.setPlaceholderText("")
                
            case _:
                self.channel_1_label.setText("Time:")
                self.channel_2_label.setText("Channel:")
                self.channel_3_label.setText("Channel:")
                self.channel_4_label.setText("Channel:")
                self.channel_2_label.setEnabled(False)
                self.channel_3_label.setEnabled(False)
                self.channel_4_label.setEnabled(False)
                
                self.channel_2_name.setEnabled(False)
                self.channel_3_name.setEnabled(False)
                self.channel_4_name.setEnabled(False)
                
                self.unit_2_label.setEnabled(False)
                self.unit_3_label.setEnabled(False)
                self.unit_4_label.setEnabled(False)
                
                self.channel_1_unit.setEnalbed(False)
                self.channel_2_unit.setEnabled(False)
                self.channel_3_unit.setEnabled(False)
                self.channel_4_unit.setEnabled(False)
                
                self.channel_1_unit.setPlaceholderText("")
                self.channel_2_unit.setPlaceholderText("")
                self.channel_3_unit.setPlaceholderText("")
                self.channel_4_unit.setPlaceholderText("")
                
    def update_values(self):
        match self.dataComboBox.currentIndex():
            case 0:
                
                self.experiment_parameters_ui['temperature_name']['ch_A'] = self.channel_1_name.text()
                self.experiment_parameters_ui['temperature_name']['ch_B'] = self.channel_2_name.text()
                self.experiment_parameters_ui['temperature_name']['ch_C'] = self.channel_3_name.text()
                self.experiment_parameters_ui['temperature_name']['ch_D'] = self.channel_4_name.text()
                
                self.experiment_parameters_ui['temperature_unit']['ch_A'] = self.channel_1_unit.text()
                self.experiment_parameters_ui['temperature_unit']['ch_B'] = self.channel_2_unit.text()
                self.experiment_parameters_ui['temperature_unit']['ch_C'] = self.channel_3_unit.text()
                self.experiment_parameters_ui['temperature_unit']['ch_D'] = self.channel_4_unit.text()
                
                
            case 1:
                self.experiment_parameters_ui['resistance_name']['ch_A'] = self.channel_1_name.text()
                self.experiment_parameters_ui['resistance_name']['ch_B'] = self.channel_2_name.text()
                self.experiment_parameters_ui['resistance_name']['ch_C'] = self.channel_3_name.text()
                self.experiment_parameters_ui['resistance_name']['ch_D'] = self.channel_4_name.text()
                
                self.experiment_parameters_ui['resistance_unit']['ch_A'] = self.channel_1_unit.text()
                self.experiment_parameters_ui['resistance_unit']['ch_B'] = self.channel_2_unit.text()
                self.experiment_parameters_ui['resistance_unit']['ch_C'] = self.channel_3_unit.text()
                self.experiment_parameters_ui['resistance_unit']['ch_D'] = self.channel_4_unit.text()
                
            case 2:
                self.experiment_parameters_ui['lockIn_name']['x'] = self.channel_1_name.text()
                self.experiment_parameters_ui['lockIn_name']['y'] = self.channel_2_name.text()
                self.experiment_parameters_ui['lockIn_name']['r'] = self.channel_3_name.text()
                self.experiment_parameters_ui['lockIn_name']['theta'] = self.channel_4_name.text()
                
                self.experiment_parameters_ui['lockIn_unit']['x'] = self.channel_1_unit.text()
                self.experiment_parameters_ui['lockIn_unit']['y'] = self.channel_2_unit.text()
                self.experiment_parameters_ui['lockIn_unit']['r'] = self.channel_3_unit.text()
                self.experiment_parameters_ui['lockIn_unit']['theta'] = self.channel_4_unit.text()
            
            case 3:
                self.experiment_parameters_ui['lockIn2_name']['x'] = self.channel_1_name.text()
                self.experiment_parameters_ui['lockIn2_name']['y'] = self.channel_2_name.text()
                self.experiment_parameters_ui['lockIn2_name']['r'] = self.channel_3_name.text()
                self.experiment_parameters_ui['lockIn2_name']['theta'] = self.channel_4_name.text()
                
                self.experiment_parameters_ui['lockIn2_unit']['x'] = self.channel_1_unit.text()
                self.experiment_parameters_ui['lockIn2_unit']['y'] = self.channel_2_unit.text()
                self.experiment_parameters_ui['lockIn2_unit']['r'] = self.channel_3_unit.text()
                self.experiment_parameters_ui['lockIn2_unit']['theta'] = self.channel_4_unit.text()
            
            case 4:
                self.experiment_parameters_ui['field_name']['field'] = self.channel_1_name.text()
        
                self.experiment_parameters_ui['field_unit']['field'] = self.channel_1_unit.text()
                
            case 5:
                self.experiment_parameters_ui['current_name']['current'] = self.channel_1_name.text()
        
                self.experiment_parameters_ui['current_unit']['current'] = self.channel_1_unit.text()
            case 6:
                self.experiment_parameters_ui['time_name']['time'] = self.channel_1_name.text()
        
                
            case _:
                pass
            
    def clear_lineEdit(self):
            self.channel_1_name.setText("")
            self.channel_2_name.setText("")
            self.channel_3_name.setText("")
            self.channel_4_name.setText("")
            
            self.channel_1_unit.setText("")
            self.channel_2_unit.setText("")
            self.channel_3_unit.setText("")
            self.channel_4_unit.setText("")
            
    def change_lineEdit(self):
        match self.dataComboBox.currentIndex():
            case 0:
                self.channel_1_name.setText(self.experiment_parameters_ui['temperature_name']['ch_A'])
                self.channel_2_name.setText(self.experiment_parameters_ui['temperature_name']['ch_B'])
                self.channel_3_name.setText(self.experiment_parameters_ui['temperature_name']['ch_C'])
                self.channel_4_name.setText(self.experiment_parameters_ui['temperature_name']['ch_D'])
                
                self.channel_1_unit.setText(self.experiment_parameters_ui['temperature_unit']['ch_A'])
                self.channel_2_unit.setText(self.experiment_parameters_ui['temperature_unit']['ch_B'])
                self.channel_3_unit.setText(self.experiment_parameters_ui['temperature_unit']['ch_C'])
                self.channel_4_unit.setText(self.experiment_parameters_ui['temperature_unit']['ch_D'])
                
            case 1:
                self.channel_1_name.setText(self.experiment_parameters_ui['resistance_name']['ch_A'])
                self.channel_2_name.setText(self.experiment_parameters_ui['resistance_name']['ch_B'])
                self.channel_3_name.setText(self.experiment_parameters_ui['resistance_name']['ch_C'])
                self.channel_4_name.setText(self.experiment_parameters_ui['resistance_name']['ch_D'])
                
                self.channel_1_unit.setText(self.experiment_parameters_ui['resistance_unit']['ch_A'])
                self.channel_2_unit.setText(self.experiment_parameters_ui['resistance_unit']['ch_B'])
                self.channel_3_unit.setText(self.experiment_parameters_ui['resistance_unit']['ch_C'])
                self.channel_4_unit.setText(self.experiment_parameters_ui['resistance_unit']['ch_D'])
                
            case 2:
                self.channel_1_name.setText(self.experiment_parameters_ui['lockIn_name']['x'])
                self.channel_2_name.setText(self.experiment_parameters_ui['lockIn_name']['y'])
                self.channel_3_name.setText(self.experiment_parameters_ui['lockIn_name']['r'])
                self.channel_4_name.setText(self.experiment_parameters_ui['lockIn_name']['theta'])
                
                self.channel_1_unit.setText(self.experiment_parameters_ui['lockIn_unit']['x'])
                self.channel_2_unit.setText(self.experiment_parameters_ui['lockIn_unit']['y'])
                self.channel_3_unit.setText(self.experiment_parameters_ui['lockIn_unit']['r'])
                self.channel_4_unit.setText(self.experiment_parameters_ui['lockIn_unit']['theta'])
                
            case 3:
                self.channel_1_name.setText(self.experiment_parameters_ui['lockIn2_name']['x'])
                self.channel_2_name.setText(self.experiment_parameters_ui['lockIn2_name']['y'])
                self.channel_3_name.setText(self.experiment_parameters_ui['lockIn2_name']['r'])
                self.channel_4_name.setText(self.experiment_parameters_ui['lockIn2_name']['theta'])
                
                self.channel_1_unit.setText(self.experiment_parameters_ui['lockIn2_unit']['x'])
                self.channel_2_unit.setText(self.experiment_parameters_ui['lockIn2_unit']['y'])
                self.channel_3_unit.setText(self.experiment_parameters_ui['lockIn2_unit']['r'])
                self.channel_4_unit.setText(self.experiment_parameters_ui['lockIn2_unit']['theta'])
            
            case 4:
                self.channel_1_name.setText(self.experiment_parameters_ui['field_name']['field'])
                self.channel_1_unit.setText(self.experiment_parameters_ui['field_name']['field'])
            
            case 5:
                self.channel_1_name.setText(self.experiment_parameters_ui['current_name']['current'])
                self.channel_1_unit.setText(self.experiment_parameters_ui['current_name']['current'])
            
            case 6:
                self.channel_1_name.setText(self.experiment_parameters_ui['time_name']['time'])
                
            case _:
                pass