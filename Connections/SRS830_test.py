import pyvisa



rm = pyvisa.ResourceManager()
print(rm.list_resources())

instrument = rm.open_resource('GPIB::8::INSTR')

instrument.write("*IDN?")
identification = instrument.query("*IDN?")
print(identification)

instrument.close()

# class SRS830_LockIn():
    
#     def __init__(self):
#         rm = pyvisa.ResourceManager()
#         print(rm.list_resources())
#         self.instrument = rm.open_resource('GPIB0::8::INSTR')
#         identification = self.instrument.query("*IDN?")
#         print(identification)
#         self.instrument.close()
        

# if __name__ == "__main__":
#     device = SRS830_LockIn()