


class Dataset:
    def __init__(self):
        
        self.temperatures = {'ch_A':[], 'ch_B':[], 'ch_C':[], 'ch_D':[]}
        self.resistances = {'ch_A':[], 'ch_B':[], 'ch_C':[], 'ch_D':[]}
        self.lockIn = {'x':[], 'y':[], 'r':[], 'theta':[]}
        self.lockIn2 = {'x':[], 'y':[], 'r':[], 'theta':[]}
        self.fields = {'field': []}
        self.currents = {'current':[]}
        self.times = {'time':[]}
        
        self.set = {'temperatures':self.temperatures, 'resistances':self.resistances, 'lockIn':self.lockIn, 'lockIn2':self.lockIn2, 'fields':self.fields, 'currents':self.currents, 'times':self.times}
        
    def clear(self):
        
        for dic in self.set.values():
            for lis in dic.values():
                lis.clear()