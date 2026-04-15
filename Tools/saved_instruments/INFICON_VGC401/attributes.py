import sys
sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')
from Tools.saved_instruments.INFICON_VGC401.methods import pressure_read_method
data_type = {}
data_unit = {}
functions = {'pressure_read': pressure_read_method.pressure_read}
read_functions = {'pressure_read': pressure_read_method.pressure_read}
write_functions = {}
data_functions = {}
initial_state = {}
