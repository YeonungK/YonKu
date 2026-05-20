


class Dataset:
    def __init__(self):
        self.set = {
            "time": {
                "time": []
            }
        }

        
        # self.temperature = {'ch_A':[], 'ch_B':[], 'ch_C':[], 'ch_D':[]}
        # self.resistance = {'ch_A':[], 'ch_B':[], 'ch_C':[], 'ch_D':[]}
        # self.lockIn = {'x':[], 'y':[], 'r':[], 'theta':[]}
        # self.lockIn2 = {'x':[], 'y':[], 'r':[], 'theta':[]}
        # self.field = {'field': []}
        # self.current = {'current':[]}
        # self.time = {'time':[]}
        
        # self.set = {'temperature':self.temperature, 'resistance':self.resistance, 'lockIn':self.lockIn, 'lockIn2':self.lockIn2, 'field':self.field, 'current':self.current, 'time':self.time}

    def build_from_instruments(self, instruments):
        """
        Build dataset from connected instruments.

        instruments:
            dict[device_key] = instrument instance

        Each instrument should expose:
            instrument.data_type = {
                "temperature": ["ch_A", "ch_B"],
                "voltage": ["value"]
            }
        """

        self.set = {
            "time": {
                "time": []
            }
        }

        for device_key, instrument in instruments.items():
            for data_type, channels in instrument.data_type.items():
                self.set.setdefault(data_type, {})

                for channel in channels:
                    self.set[data_type].setdefault(channel, [])

        return self.set

    def clear(self):
        
        for dic in self.set.values():
            for lis in dic.values():
                lis.clear()