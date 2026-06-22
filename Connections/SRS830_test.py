import pyvisa



rm = pyvisa.ResourceManager()
print(rm.list_resources())

instrument = rm.open_resource('GPIB::8::INSTR')

instrument.write("*IDN?")
identification = instrument.query("*IDN?")
print(identification)

instrument.close()

    
        

