# -*- coding: utf-8 -*-
"""
Created on Thu May 22 16:02:29 2025

@author: szkop
"""

import serial, time

device = serial.Serial('COM4', 
                    baudrate=57600, 
                    bytesize=serial.SEVENBITS, 
                    parity=serial.PARITY_ODD, 
                    stopbits = serial.STOPBITS_ONE)

command = "*IDN?\n"
device.write(command.encode('ascii'))
time.sleep(0.1)

if device.in_waiting > 0:
    response = device.readline().decode('ascii').strip()
    print(f"Response: {response}")
else:
    print("No response received")



device.close()