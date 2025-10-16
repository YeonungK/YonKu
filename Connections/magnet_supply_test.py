# -*- coding: utf-8 -*-
"""
Created on Tue May 27 17:54:39 2025

@author: szkop
"""

import socket

TIMEOUT_VAL = 20000

instr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

IPV4 = "169.254.107.99"
PORT = 7020

instr.connect((IPV4, PORT))