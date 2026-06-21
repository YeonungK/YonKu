#{'name': 'lockInAmplifier2', 'interface': 'gpib', 'model': 'SRS_830_2', 'address': '15'}        

import pyvisa
import time
import sys

sys.path.append('C:/Users/szkop/OneDrive/Desktop/YonKu')

from Tools.Instrument import GPIBInstrument
from Tools.saved_instruments.SRS_830_2 import attributes


class lockInAmplifier2(GPIBInstrument):
    def __init__(self, name, address):
        super().__init__(name, 'SRS_844', address)
        self.data_type = attributes.data_type
        self.data_label = attributes.data_label
        self.data_unit = attributes.data_unit
        self.data_function = attributes.data_functions
        self.read_functions = attributes.read_functions
        self.write_functions = attributes.write_functions
        self.initial_state = attributes.initial_state
        
        
        self.tauset={
                "10 u" : 0,
                "30 u" : 1,
                "100 u" : 2,
                "300 u" : 3,
                "1 m" : 4,
                "3 m" : 5,
                "10 m" : 6,
                "30 m" : 7,
                "100 m" : 8,
                "300 m" : 9,
                "1" : 10,
                "3" : 11,
                "10" : 12,
                "30" : 13,
                "100" : 14,
                "300" : 15,
                "1 k" : 16,
                "3 k" : 17,
                "10 k" : 18,
                "30 k" : 19}
        self.sensset={
                "2 n" : 0,
                "5 n" : 1,
                "10 n" : 2,
                "20 n" : 3,
                "50 n" : 4,
                "100 n" : 5,
                "200 n" : 6,
                "500 n" : 7,
                "1 u" : 8,
                "2 u" : 9,
                "5 u" : 10,
                "10 u" : 11,
                "20 u" : 12,
                "50 u" : 13,
                "100 u" : 14,
                "200 u" : 15,
                "500 u" : 16,
                "1 m" : 17,
                "2 m" : 18,
                "5 m" : 19,
                "10 m" : 20,
                "20 m" : 21,
                "50 m" : 22,
                "100 m" : 23,
                "200 m" :  24,
                "500 m" : 25,
                "1" : 26}
        
    def reset(self):
        self.write('*RST')
    def identification(self):
        msg = self.query('*IDN?')
        return msg
    def clear(self):
        self.write('*CLS')
    def disable_front_panel(self):
        self.write('OVRM 1')
    def enable_front_panel(self):
        self.write('OVRM 0')
    def auto_phase(self):
        self.write('APHS')
    def auto_gain(self):
        self.write('AGAN')
    def auto_reserve(self):
        self.write('ARSV')
    def auto_offset(self,channel):
        self.write('AOFF %i' % channel )
        
    #get settings
    def get_tau(self):
        return self.query('OFLT?')   
    def get_sens(self):
        return self.query('SENS?')   
    def get_trigsource(self):
        return self.query('FMOD?')
    def get_trigshape(self):
        return self.query('RSLP?')
    def get_harm(self):
        return self.query('HARM?')
    def get_input(self):
        return self.query('ISRC?')
    def get_ground(self):
        return self.query('IGND?')
    def get_couple(self):
        return self.query('ICPL?')
    def get_filter(self):
        return self.query('ILIN?')
    def get_reserve(self):
        return self.query('RMOD?')
    def get_slope(self):
        return self.query('OFSL?')
    def get_sync(self):
        return self.query('SYNC?')
    def get_disp_rat(self,channel):
        return self.query('DDEF? %i' % channel)
    def get_exp_off(self,channel):
        return self.query('OEXP? %i' % channel)

    #set settings        
    def set_freq(self,freq):
        self.write('FREQ %f' % freq )
    def set_ampl(self,ampl):
        self.write('SLVL %f' % ampl)
    def set_mode(self,mode):
        self.write('FMOD %i' % mode)
    def set_tau(self,tau):
        self.write('OFLT %i' % tau)
    def set_sens(self,sens):
        self.write('SENS %i' % sens)    
    def set_phase(self,phase):
        self.write('PHAS %f' % phase)       
    def set_aux(self,output,value):
        self.write('AUXV %(out)i, %(val).3f' % {'out':output,'val':value})
    def set_trigsource(self,ref):
        self.write('FMOD %e' % ref)
    def set_trigshape(self, trigshape):
        self.write('RSLP %i' % trigshape)        
    def set_disp_rat(self,channel,disp,ratio):
        self.write('DDEF %(channel)i, %(disp)i, %(ratio)i'  % {'channel':channel,'disp':disp, 'ratio':ratio})
    def set_exp_off(self,channel,offset,expand):
        self.write('OEXP %(channel)i, %(offset)f, %(expand)i'  % {'channel':channel,'offset':offset, 'expand':expand})
    def set_reserve(self,reserve):
        self.write('RMOD %i' % reserve)
    def set_filter(self,filt):
        self.write('ILIN %i' % filt)
    def set_input(self, inp):
        self.write('ISRC %i' % inp)
    def set_ground(self,gnd):
        self.write('IGND %i' % gnd)
    def set_couple(self, coup):
        self.write('ICPL %i' % coup)
    def set_slope(self,slope):
        self.write('OFSL %i' % slope)
    def set_sync(self,sync):
        self.write('SYNC %i' % sync)
    def set_harm(self,harm):
        self.write('HARM %i' % harm)        
        
    #get data    
    def get_all(self):
        result = self.query("SNAP? 1,2,3,4")
        result = result.split(",")
        for i in range(4):
            result[i] = float(result[i])
        return result
    def get_X(self):
        return float(self.query('OUTP? 1'))
    def get_Y(self):
        return float(self.query('OUTP? 2'))
    def get_R(self):
        return float(self.query('OUTP? 3'))
    def get_Theta(self):
        return float(self.query('OUTP? 4'))
    def get_freq(self):
        return float(self.query('FREQ?'))   
    def get_ampl(self):
        return float(self.query('SLVL?'))        
    def get_phase(self):
        return float(self.query('PHAS?'))
    def get_harm(self):
        return float(self.query('HARM?'))
    def get_oaux(self,value):
        return float(self.query('OAUX? %i' %value))
    def read_aux(self,output):
        return float(self.query('AUXV? %i' %output))
    
    
if __name__ == "__main__":
    device = lockInAmplifier1('test', 8)
    msg = device.get_trigsource()
    print(msg)
    