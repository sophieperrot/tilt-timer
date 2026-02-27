#!/usr/bin/env python3
"""CODE FOR DISPLAY"""

import time
import threading
from gpiozero import OutputDevice


# 74HC595 pins
DATA_PIN = 24 # DS pin
LATCH_PIN = 23 # ST_CP pin
CLOCK_PIN = 18 # SH_CP pin
# GPIO pins
DIGIT_PINS = (17, 27, 22, 10)
# Encoding for 0-9 (common anode)
SEGMENT_CODES = (0xc0, 0xf9, 0xa4, 0xb0, 0x99, 
                 0x92, 0x82, 0xf8, 0x80, 0x90)
CLEAR_DISPLAY = 0xff


class SevenSegmentDisplay:
	def __init__(self):
		# Initialise hardware
		self.data_pin = OutputDevice(DATA_PIN)
		self.latch_pin = OutputDevice(LATCH_PIN)
		self.clock_pin = OutputDevice(CLOCK_PIN)
		self.digits = [OutputDevice(pin) for pin in DIGIT_PINS
		
		self.counter = 0
		self.running = True
