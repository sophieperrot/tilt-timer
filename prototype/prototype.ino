// Basic demo for accelerometer readings from Adafruit MPU6050

#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

Adafruit_MPU6050 mpu;

const char* faceNames[] = {"bottom (z+)", "top (z-)", "right (x+)",
                         "left (x-)", "front (y+)", "back (y-)"};
const unsigned long faceDurations[6] = {
  60000, // bottom (z+) - 60 sec
  15000, // top (z-)
  30000, // right (x+)
  5000, // left (x-)
  0, // front (y+) is nothing
  0, // back (y-) is pause timer
};
int currentFace = -1;
bool timerRunning = false;
unsigned long faceStableSince;
unsigned long timerDuration;
unsigned long timerStartTime;
unsigned long timerEndTime;
unsigned long lastDisplayTime = 0;

int getDownFace() {
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  float ax = a.acceleration.x;
  float ay = a.acceleration.y;
  float az = a.acceleration.z;

  float maxVal = ax;
  int maxAxis = 0;
  if (ay > maxVal) { maxVal = ay; maxAxis = 1; }
  if (az > maxVal) { maxVal = az; maxAxis = 2; }

  if (maxAxis == 2) {
    return (maxVal > 0) ? 0 : 1;
  } else if (maxAxis == 0) {
    return (maxVal > 0) ? 2 : 3;
  } else {
    return (maxVal > 0) ? 4 : 5;
  }
}

void endTimer(int newFace) {
  currentFace = newFace;
  faceStableSince = millis();
  if (timerRunning) {
    Serial.println(faceNames[currentFace]);
    Serial.println("Face change detected, current timer cancelled.");
    timerRunning = false;
  }
}

void pauseTimer(int pauseFace, int timerFace) {
  Serial.println("timer paused");
  Serial.print("pause face: ");
  Serial.println(faceNames[pauseFace]);
  Serial.print("current face:");
  Serial.println(faceNames[currentFace]);
  unsigned long pauseStartTime = millis();
  timerRunning = false;
  currentFace = pauseFace;
  int newFace = currentFace;
  while (newFace == pauseFace) {
    newFace = getDownFace();
    if (newFace == timerFace) {
      timerEndTime += millis() - pauseStartTime;
      currentFace = newFace;
      timerRunning = true;
      break;
    } else if (newFace != pauseFace) {
      endTimer(newFace);
      break;
    }
    delay(20);
  }
}

void setup(void) {
  Serial.begin(115200);
  while (!Serial);

  // Try to initialize!
  if (!mpu.begin()) {
    Serial.println("MPU6050 not found");
    while (1) {
      delay(10);
    }
  }

  mpu.setAccelerometerRange(MPU6050_RANGE_16_G);
  mpu.setGyroRange(MPU6050_RANGE_250_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  Serial.println("\nPlace cube on a face to start timer.");
  delay(100);
}

void loop() {
  int newFace = getDownFace();
  unsigned long now = millis();

  if (newFace == 4 || newFace == 5) {
    int bufferFace = getDownFace();
    if (bufferFace != currentFace) {
      pauseTimer(newFace, currentFace);
    }
  } else if (newFace != currentFace) {
    int bufferFace = getDownFace();
    if (bufferFace != currentFace) {
      endTimer(newFace);
    }
  } else {
    if (!timerRunning && (now - faceStableSince > 1000)) {
      timerDuration = faceDurations[currentFace];
      timerStartTime = now;
      timerEndTime = now + timerDuration;
      timerRunning = true;
      Serial.printf("%s face timer started: %lu s\n", faceNames[currentFace], timerDuration/1000);
    }
  }

  if (timerRunning) {
    if (now >= timerEndTime) {
      timerRunning = false;
      Serial.println("TIME'S UP!");
    } else {
      if (now - lastDisplayTime >= 1000) {
        lastDisplayTime = now;
        unsigned long timeRemaining = timerEndTime - now;
        Serial.printf("%lu\n", timeRemaining/1000);
        // Serial.printf("Face down: %-12s | X:%6.2f Y=6.2f Z:6.2f m/s^2\n",
        //                faceNames[currentFace], ax, ay, az);
      }
    }
  }
  delay(20);
}