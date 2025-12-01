import pandas as pd
import time
import sys
import numpy as np
from pathlib import Path


class DataLogger:
    def __init__(self, instruments, data_set, title):
        
        # try:
        self.title = title
        self.instruments = instruments
        self.concat_list = []
        self.keys = []
        
        
        for device_model, instrument in self.instruments.items():
            for data_type in instrument.data_type.keys():
                print(f"instrument data type: {data_type}")
                logging_data = setattr(self, f"df_{data_type}", pd.DataFrame.from_dict(data_set[f'{data_type}']))
                logging_data = getattr(self, f"df_{data_type}")
                self.concat_list.append(logging_data)
                self.keys.append(f'{data_type}')
        
        self.df_times = pd.DataFrame.from_dict(data_set['time'])        
        self.concat_list.append(self.df_times)
        self.keys.append('time')
        print(self.keys)
                
        # self.df_temperatures = pd.DataFrame.from_dict(data_set['temperatures'])
        # self.df_resistances = pd.DataFrame.from_dict(data_set['resistances'])
        # self.df_lockIn = pd.DataFrame.from_dict(data_set['lockIn'])
        # self.df_lockIn2 = pd.DataFrame.from_dict(data_set['lockIn2'])
        # self.df_fields = pd.DataFrame.from_dict(data_set['fields'])
        # self.df_currents = pd.DataFrame.from_dict(data_set['currents'])
        # self.df_times = pd.DataFrame.from_dict(data_set['times'])
        
        self.result = pd.concat(self.concat_list, axis=1, keys=self.keys)

        print(self.result)
    # self.path = Path(f'C:/Users/szkop/Desktop/YonKu/Data/{self.title}.csv')
    
        self.result.to_csv(f'C:/Users/szkop/OneDrive/Desktop/YonKu/Data/experiment_data/{self.title}.csv', index=False)
        
        # except KeyError:
        #     print("Check the keys in the dataset.")
        
        
        

    def append(self, logging_data_list):
        
        self.concat_list = []
        list_index = 0
        data_index = 0
        print(logging_data_list)
        print(self.instruments)
        
        for device_model, instrument in self.instruments.items():
            for data_type in instrument.data_type.keys():
                data_index = 0
                appending_dict = setattr(self, f'appending_{data_type}', {})
                appending_dict = getattr(self, f'appending_{data_type}')
                print(appending_dict)
                for data_ch in instrument.data_type[data_type]:
                    appending_dict[data_ch] = [logging_data_list[list_index][data_index]]
                    data_index += 1
                    print(appending_dict)
            
                self.concat_list.append(pd.DataFrame.from_dict(appending_dict))
                
                list_index += 1
        
        data_index = 0
        appending_times = {'time':[]}
        appending_times['time'].append(logging_data_list[list_index])
        print(appending_times)         
        self.df_times = pd.DataFrame.from_dict(appending_times)        
        self.concat_list.append(self.df_times)
        print(self.concat_list)
                
        # appending_temperatures = {'ch_A':[], 'ch_B':[], 'ch_C':[], 'ch_D':[]}
        # appending_resistances = {'ch_A':[], 'ch_B':[], 'ch_C':[], 'ch_D':[]}
        # appending_lockIn = {'x':[], 'y':[], 'r':[], 'theta':[]}
        # appending_lockIn2 = {'x':[], 'y':[], 'r':[], 'theta':[]}
        # appending_fields = {'field':[]}
        # appending_currents = {'current':[]}
        # appending_times = {'time':[]}
        
        # appending_temperatures['ch_A'].append(temp_list[0])
        # appending_temperatures['ch_B'].append(temp_list[1])
        # appending_temperatures['ch_C'].append(temp_list[2])
        # appending_temperatures['ch_D'].append(temp_list[3])
        
        # appending_resistances['ch_A'].append(resist_list[0])
        # appending_resistances['ch_B'].append(resist_list[1])
        # appending_resistances['ch_C'].append(resist_list[2])
        # appending_resistances['ch_D'].append(resist_list[3])
        
        # appending_lockIn['x'].append(lockIn_list[0])
        # appending_lockIn['y'].append(lockIn_list[1])
        # appending_lockIn['r'].append(lockIn_list[2])
        # appending_lockIn['theta'].append(lockIn_list[3])
        
        # appending_lockIn2['x'].append(lockIn2_list[0])
        # appending_lockIn2['y'].append(lockIn2_list[1])
        # appending_lockIn2['r'].append(lockIn2_list[2])
        # appending_lockIn2['theta'].append(lockIn2_list[3])
        
        # appending_fields['field'].append(field_list)
        
        # appending_currents['current'].append(current_list)
        
        # appending_times['time'].append(now)
        
        # df_a_temperatures = pd.DataFrame.from_dict(appending_temperatures)
        # df_a_resistances = pd.DataFrame.from_dict(appending_resistances)
        # df_a_lockIn = pd.DataFrame.from_dict(appending_lockIn)
        # df_a_lockIn2 = pd.DataFrame.from_dict(appending_lockIn2)
        # df_a_fields = pd.DataFrame.from_dict(appending_fields)
        # df_a_currents = pd.DataFrame.from_dict(appending_currents)
        # df_a_times = pd.DataFrame.from_dict(appending_times)
        
        result = pd.concat(self.concat_list, axis=1, keys=self.keys)
        
        result.to_csv(f'C:/Users/szkop/OneDrive/Desktop/YonKu/Data/experiment_data/{self.title}.csv', mode = 'a', index=False, header = False)


class ErrorLogger:
    def __init__(self, heading, title):
        self.title = title
        self.heading = heading
        self.file_path = Path(f"C:/Users/szkop/OneDrive/Desktop/YonKu/Data/error_log/{self.title}.txt")
        # self.file_path.mkdir(parents=True, exist_ok=True)
        # self.file = open(self.file_path, "x")
        with open(self.file_path, "w") as f:
            f.write(self.heading)
            f.close()
        
    def append(self, msg):
        with open(self.file_path, "a") as f:
            f.write(msg)
            f.close()

if __name__ == "__main__":
    
    temperatures = {'ch_A':[1,2,3], 'ch_B':[2,3,4], 'ch_C':[5,6,7], 'ch_D':[8,7,5]}
    resistances = {'ch_A':[5,6,7], 'ch_B':[1,4,5], 'ch_C':[4,7,6], 'ch_D':[3,4,6]}
    voltages = {'ch_A':[], 'ch_B':[], 'ch_C':[], 'ch_D':[]}
    times = {'time':[1,2,3]}
    
    data_set = [temperatures, resistances, voltages, times]

    
    datalog = DataLogger(data_set, 'experiment')
    
    print(datalog.result)
        
        
