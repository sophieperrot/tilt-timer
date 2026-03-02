#!/usr/bin/env python3
"""CODE FOR DETECTING MOVEMENT/STATE WITH ACCELEROMETER (MPU6050RAW)"""

from mpu6050 import mpu6050
import time

sensor = mpu6050(0x68)

DATA_THRESHOLD = 8.0 # g but accounted for tilting
CONFIDENCE_THRESHOLD = 10 # must be in new state for this num of cycles to update
ORIENTATION = {"TOP": 1, "BOTTOM": 2, "LEFT": 3, 
                    "RIGHT": 4, "FRONT": 5, "BACK": 6}


class OrientationDetector:
	def __init__(self):
		self.current_state = "UNKNOWN"
		self.pending_state = 0
		self.confidence_counter = 0
	
	def get_orientation(self):
		"""Returns orientation based on which axis feels the most g"""
		data = sensor.get_accel_data()
		x, y, z = data['x'], data['y'], data['z']
		
		if z > DATA_THRESHOLD: return ORIENTATION["TOP"]
		if z < -DATA_THRESHOLD: return ORIENTATION["BOTTOM"]
		if x > DATA_THRESHOLD: return ORIENTATION["LEFT"]
		if x < -DATA_THRESHOLD: return ORIENTATION["RIGHT"]
		if y > DATA_THRESHOLD: return ORIENTATION["FRONT"]
		if y < -DATA_THRESHOLD: return ORIENTATION["BACK"]
	
		return None
	
	def update(self):
		"""Returns True if state is officially changed (processes hysteresis)"""
		reading = self.get_orientation()

		if reading == self.current_state or reading is None:
			self.confidence_counter = 0
			return False
		
		if reading == self.pending_state:
			self.confidence_counter += 1
		else:
			self.pending_state = reading
			self.confidence_counter = 1
		
		if self.confidence_counter >= CONFIDENCE_THRESHOLD:
			self.current_state = self.pending_state
			self.confidence_counter = 0
			return True
		
		return False



if __name__ == "__main__":
	detector = OrientationDetector()
	try:
		while True:
			if detector.update():
				print(f"Stable state: {detector.current_state}")
			time.sleep(0.05) # 20 Hz sampling freq
	except KeyboardInterrupt:
		print("Orientation detection program ending")
