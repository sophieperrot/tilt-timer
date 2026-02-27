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


class SevenSegmentClock:
	def __init__(self):
		# Initialise hardware
		self.data_pin = OutputDevice(DATA_PIN)
		self.latch_pin = OutputDevice(LATCH_PIN)
		self.clock_pin = OutputDevice(CLOCK_PIN)
		self.digits = [OutputDevice(pin) for pin in DIGIT_PINS
		
		self.counter = 0
		self.running = True
		
	def _shift_out(self, val):
		"""Sends 8 bits to 74HC595"""
		for i in range(8):
			self.clock_pin.off()
			# MSBFIRST logic (check leftmost bit first)
			if 0x80 & (val << i):
				self.data_pin.on()
			else:
				self.data_pin.off()
			self.clock_pin.on()
	
	def _update_hardware(self, segment_hex, digit_index):
		"""Updates one digit on display"""
		# Blanking (turning off all digits to prevent ghosting)
		for digit_obj in self.digits:
			digit_obj.on()
		
		# Prepare segments
		self.latch_pin.off()
		self._shift_out(segment_hex)
		self.latch_pin.on()
		
		# Activate correct digit (common anode: off=active)
		for i, digit_obj in enumerate(self, digits):
			if i == digit_index:
				digit_obj.off()
			else:
				digit_obj.on()
				
		time.sleep(0.003) # for vision delay
	
	def increment_timer(self):
		"""Background thread func - increment counter every second"""
		while self.running:
			time.sleep(1.0)
			self.counter += 1
			print(f"Counter: {self.counter}")
			
	def run_display_leep(self):
		"""Main loop to refresh 4-digit display"""
		try:
			while self.running:
				# Extract digits
				val = self.counter
				display_digits = [
					SEGMENT_MAP[(val // 1000) % 10],
					SEGMENT_MAP[(val // 100) % 10],
					SEGMENT_MAP[(val // 10) % 10],
					SEGMENT_MAP[val % 10]
				]
				
				for index, segment_hex in enumerate(display_digits):
					self._update_hardware(segment_hex, index)
		except KeyboardInterrupt:
			self.stop()
	
	def stop(self):
		print("#nShutting down 4-digit seven segment display")
		self.running = False
		# Turn off segments and digits
		self.latch_pin.off()
		self._shift_out(CLEAR_DISPLAY)
		self.latch_pin.on()
		for d in self.digits:
			d.on()
		# Close pins
		self.data_pin.close()
		self.latch_pin.close()
		self.clock_pin.close()
		for d in self.digits:
			d.close()
			

if __name__ == "__main__":
	clock = SevenSegmentClock()
	
	# Start timer in a background thread
	timer_thread = threading.Thread(target=clock.increment_timer, daemon=True)
	timer_thread.start()
	
	clock.run_display_loop()
