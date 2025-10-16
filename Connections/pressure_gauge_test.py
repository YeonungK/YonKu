# -*- coding: utf-8 -*-
"""
Created on Mon May 26 17:26:13 2025

@author: szkop
"""

import serial, time

device = serial.Serial('COM5', 
                    baudrate=9600, 
                    bytesize=serial.EIGHTBITS, 
                    parity=serial.PARITY_NONE, 
                    stopbits = serial.STOPBITS_ONE)

command = "PR1\n"
device.write(command.encode('ascii'))
time.sleep(0.1)
if device.in_waiting > 0:
    response = device.readline()
    print(response)
else:
    print("no response")
    device.close()

device.write(b'\x05\n')
time.sleep(0.1)
if device.in_waiting > 0:
    response = device.readline().decode('ascii')
    print(response)
else:
    print("no response")
    device.close()

# enquiry = "PR1\n"
# device.write(enquiry.encode('ascii'))
# time.sleep(1)

# if device.in_waiting > 0:
#     response = device.readline()
#     print(response)

# else: 
#     print("No response")



# response = device.read()
# print(f"Response: {response}")
# device.write(b'\x05')
# response2 = device.readline().decode('utf-8').strip()
# print(f"Response: {response2}")


# if device.in_waiting > 0:
#     response = device.read()
#     print(f"Response: {response}")
#     device.write(b'\x05')
#     if device.in_waiting > 0:
#         response2 = device.read()
#         print(f"Response: {response}")
# else:
#     print("No response received")
    
   
device.close()