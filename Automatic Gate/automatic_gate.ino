#include <Servo.h>

// Pin definitions
const int triggerPin = 2;
const int echoPin = 3;
const int redLedAnodePin = 4;
const int redLedCathodePin = 8;
const int blueLedPin = 5;
const int blueLedCathodePin = 7;
const int servoPin = 6;
const int buzzerPin = 12;

// Constants
const float thresholdDistance = 50.0;   // cm
const int closedAngle = 0;
const int openAngle = 90;
const unsigned long closeDelay = 5000;  // 5 seconds

// Global state
Servo myServo;
bool isOpen = false;
unsigned long lastDetectionTime = 0;

void setup() {
  // Sensor pins
  pinMode(triggerPin, OUTPUT);
  pinMode(echoPin, INPUT);

  // LEDs
  pinMode(redLedAnodePin, OUTPUT);
  pinMode(redLedCathodePin, OUTPUT);
  digitalWrite(redLedCathodePin, LOW); // Act as GND

  pinMode(blueLedPin, OUTPUT);
  pinMode(blueLedCathodePin, OUTPUT);
  digitalWrite(blueLedCathodePin, LOW); // Act as GND

  // Buzzer
  pinMode(buzzerPin, OUTPUT);

  // Servo
  myServo.attach(servoPin);
  myServo.write(closedAngle); // Start closed

  // Initial LED & buzzer state
  digitalWrite(redLedAnodePin, HIGH);  // Red ON
  digitalWrite(blueLedPin, LOW);       // Blue OFF
  digitalWrite(buzzerPin, LOW);        // Buzzer OFF
}

float getDistance() {
  digitalWrite(triggerPin, LOW);
  delayMicroseconds(2);
  digitalWrite(triggerPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(triggerPin, LOW);
  long duration = pulseIn(echoPin, HIGH);
  return duration / 58.0;  // Convert to cm
}

void loop() {
  float distance = getDistance();
  bool objectDetected = (distance < thresholdDistance);

  if (objectDetected) {
    if (!isOpen) {
      // Open gate
      myServo.write(openAngle);
      isOpen = true;
      digitalWrite(redLedAnodePin, LOW);   // Red OFF
      digitalWrite(blueLedPin, HIGH);      // Blue ON
    }
    digitalWrite(buzzerPin, HIGH);         // Buzzer ON
    lastDetectionTime = millis();
  } else {
    if (isOpen && (millis() - lastDetectionTime > closeDelay)) {
      // Close gate
      myServo.write(closedAngle);
      isOpen = false;
      digitalWrite(redLedAnodePin, HIGH);  // Red ON
      digitalWrite(blueLedPin, LOW);       // Blue OFF
      digitalWrite(buzzerPin, LOW);        // Buzzer OFF
    }
  }

  delay(100);
}
