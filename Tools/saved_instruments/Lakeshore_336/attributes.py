import sys
sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')
from Tools.saved_instruments.Members.Lakeshore_336 import attributes, read_temp_method
data_type = {}
data_unit = {}
functions = {'read_temp': read_temp_method.read_temp}
read_functions = {'read_temp': read_temp_method.read_temp}
write_functions = {}
data_functions = {}
initial_state = {}
