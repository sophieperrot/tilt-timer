#!/usr/bin/env python3
"""CODE FOR 4-DIGIT SEVEN SEGMENT DISPLAY (74HC595)"""

import time
import threading
from gpiozero import OutputDevice


# 74HC595 pins
DATA_PIN = 24 # DS pin
LATCH_PIN = 23 # ST_CP pin
CLOCK_PIN = 18 # SH_CP pin
# GPIO pins
DIGIT_PINS = (17, 27, 22, 10)
# Segment codes for 0-9 (common anode)
SEGMENT_MAP = (0xc0, 0xf9, 0xa4, 0xb0, 0x99, 
                 0x92, 0x82, 0xf8, 0x80, 0x90)
CLEAR_DISPLAY = 0xff


class SevenSegmentDisplay:
	def __init__(self):
		# Initialise hardware
		self.data_pin = OutputDevice(DATA_PIN)
		self.latch_pin = OutputDevice(LATCH_PIN)
		self.clock_pin = OutputDevice(CLOCK_PIN)
		self.digits = [OutputDevice(pin) for pin in DIGIT_PINS]
		
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
		for i, digit_obj in enumerate(self.digits):
			if i == digit_index:
				digit_obj.off()
			else:
				digit_obj.on()
				
		time.sleep(0.003) # for vision delay
			
	def render_time(self, time):
		"""Main loop to refresh 4-digit display"""
		minutes = time // 60
		seconds = time % 60
		# Extract digits
		display_digits = [
			SEGMENT_MAP[(minutes // 10) % 10],
			SEGMENT_MAP[minutes % 10],
			SEGMENT_MAP[(seconds // 10) % 10],
			SEGMENT_MAP[seconds % 10]
		]
		
		for index, segment_hex in enumerate(display_digits):
			self._update_hardware(segment_hex, index)
	
	def stop(self):
		print("\nShutting down 4-digit seven segment display")
		
		# Turn off segments and digits
		self.latch_pin.off()
		self._shift_out(CLEAR_DISPLAY)
		self.latch_pin.on()
		for d in self.digits:
			d.on()
			d.close()
		
		# Close pins
		self.data_pin.close()
		self.latch_pin.close()
		self.clock_pin.close()
			
class Stopwatch:
	def __init__(self, display):
		self.display = display
		self.running = False
		self.counter = 0
	
	def start(self):
		"""Start background timer thread"""
		self.running = True
		self.thread = threading.Thread(target=self._tick, daemon=True)
		self.running = False

	def _tick(self):
		while self.running:
			time.sleep(1.0)
			self.counter += 1

	def run_display_loop(self):
		try:
			while self.running:
				self.display.render_time(self.counter)
		except KeyboardInterrupt:
			self.stop()

	def stop(self):
		print("Stopping timer")
		self.running = False
		self.display.stop()

class Timer(Stopwatch):
	def _tick(self):
		while self.running:
			time.sleep(1.0)
			if self.counter > 0:
				self.counter -= 1
			elif self.counter == 0:
				self.stop()

if __name__ == "__main__":
	clock = SevenSegmentDisplay()

	timer_seconds = 60 # 1 minute timer to test
	
	# Start timer in a background thread
	timer_thread = threading.Thread(target=clock.increment_timer, daemon=True)
	timer_thread.start()
	
	clock.run_display_loop()
