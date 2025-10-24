#importing modules
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit



class DataAnalyzer:
    def __init__(self, datasetLink):
        self.datasetLink = datasetLink
        self.dataset = pd.read_csv(self.datasetLink, header=[0,1])
        print(self.dataset)
        
        self.x_data = self.dataset['resistances']['ch_A'].to_list()
        self.y_data = self.dataset['temperatures']['ch_A'].to_list()
        
        
        self.dataset.plot(kind = 'scatter', x = 'resistances', y = 'temperatures')
        plt.show()
        




if __name__ == "__main__":
    test = DataAnalyzer("C:/Users/szkop/OneDrive/Desktop/YonKu/Data/data_analysis/Mag_Top_valid_data.csv")