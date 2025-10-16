import serial.tools.list_ports
import pyvisa

ports = list(serial.tools.list_ports.comports())

for port in ports:
    print(f'Device: {port.device}, Description: {port.description}')

rm = pyvisa.ResourceManager()

# List all connected instruments
resources = rm.list_resources()
print("Connected Instruments:")
for resource in resources:
    print(resource)