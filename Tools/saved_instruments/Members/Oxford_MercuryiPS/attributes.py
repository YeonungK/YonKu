import sys
sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')
from Tools.saved_instruments.Members.Oxford_MercuryiPS import attributes, temp_method
data_type = {}
data_unit = {}
functions = {'temp': temp_method.temp}
read_functions = {'temp': temp_method.temp}
write_functions = {}
data_functions = {}
initial_state = {}
