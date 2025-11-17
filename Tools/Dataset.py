


class Dataset:
    def __init__(self):
        
        self.temperature = {'ch_A':[], 'ch_B':[], 'ch_C':[], 'ch_D':[]}
        self.resistance = {'ch_A':[], 'ch_B':[], 'ch_C':[], 'ch_D':[]}
        self.lockIn = {'x':[], 'y':[], 'r':[], 'theta':[]}
        self.lockIn2 = {'x':[], 'y':[], 'r':[], 'theta':[]}
        self.field = {'field': []}
        self.current = {'current':[]}
        self.time = {'time':[]}
        
        self.set = {'temperature':self.temperature, 'resistance':self.resistance, 'lockIn':self.lockIn, 'lockIn2':self.lockIn2, 'field':self.field, 'current':self.current, 'time':self.time}
        
    def clear(self):
        
        for dic in self.set.values():
            for lis in dic.values():
                lis.clear()