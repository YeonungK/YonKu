import sys
sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')
from Tools.saved_instruments.test_model.methods import ser_method
data_type = {}
data_unit = {}
functions = {'ser': ser_method.ser}
read_functions = {'ser': ser_method.ser}
write_functions = {}
data_functions = {}
initial_state = {}
