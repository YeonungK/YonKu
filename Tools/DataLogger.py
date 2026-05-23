import pandas as pd
import time
import sys
import numpy as np
from pathlib import Path
from project_paths import EXPERIMENT_DATA_DIR, DATA_DIR


class DataLogger:
    def __init__(self, instruments, data_set, title):
        
        # try:
        self.title = title
        self.instruments = instruments
        self.concat_list = []
        self.keys = []
        
        
        for device_key, instrument in self.instruments.items():
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
                
        
        self.result = pd.concat(self.concat_list, axis=1, keys=self.keys)

        print(self.result)
    
        self.result.to_csv(EXPERIMENT_DATA_DIR / f'{self.title}.csv', index=False)
        

        

    def append(self, logging_data_list):
        
        self.concat_list = []
        list_index = 0
        data_index = 0
        # print(logging_data_list)
        # print(self.instruments)
        
        for device_key, instrument in self.instruments.items():
            for data_type in instrument.data_type.keys():
                data_index = 0
                appending_dict = setattr(self, f'appending_{data_type}', {})
                appending_dict = getattr(self, f'appending_{data_type}')
                # print(appending_dict)
                for data_ch in instrument.data_type[data_type]:
                    appending_dict[data_ch] = [logging_data_list[list_index][data_index]]
                    data_index += 1
                    # print(appending_dict)
            
                self.concat_list.append(pd.DataFrame.from_dict(appending_dict))
                
                list_index += 1
        
        data_index = 0
        appending_times = {'time':[]}
        appending_times['time'].append(logging_data_list[list_index])
        # print(appending_times)         
        self.df_times = pd.DataFrame.from_dict(appending_times)        
        self.concat_list.append(self.df_times)
        # print(self.concat_list)
        
        result = pd.concat(self.concat_list, axis=1, keys=self.keys)
        
        result.to_csv(EXPERIMENT_DATA_DIR / f'{self.title}.csv', mode = 'a', index=False, header = False)


class ErrorLogger:
    def __init__(self, heading, title):
        self.title = title
        self.heading = heading
        self.file_path = Path(f"{DATA_DIR}/error_log/{self.title}.txt")
        # self.file_path.mkdir(parents=True, exist_ok=True)
        # self.file = open(self.file_path, "x")
        with open(self.file_path, "w") as f:
            f.write(self.heading)
            f.close()
        
    def append(self, msg):
        with open(self.file_path, "a") as f:
            f.write(msg)
            f.close()

