# -*- coding: utf-8 -*-
"""
Created on Mon May 26 12:32:30 2025

@author: szkop
"""

"""Example for generating digital signals.

This example demonstrates how to write values to a digital
output channel.
"""

import nidaqmx
import nidaqmx.system
from nidaqmx.constants import LineGrouping

system = nidaqmx.system.System.local()
for device in system.devices:
    print(device)

with nidaqmx.Task() as task:
    # The values in the list refers to the data for pin 0, 1, 2 respectively
    data = [True, True, True]
    data2 = [False, False, False]

    task.do_channels.add_do_chan("Dev1/port0/line0:2", line_grouping=LineGrouping.CHAN_PER_LINE)
    task.start()
    task.write(data2)
    task.stop()