# Arduino Gate Control System with Ultrasonic Sensor

This project demonstrates an automated gate control system using an ultrasonic sensor, servo motor, LEDs, and a buzzer. The system detects objects within a certain distance and opens or closes the gate accordingly.

## Components Used
- **Ultrasonic Sensor (HC-SR04)**: Measures the distance to detect objects.
- **Servo Motor**: Controls the gate's opening and closing.
- **Red LED**: Indicates the gate is closed.
- **Blue LED**: Indicates the gate is open.
- **Buzzer**: Alerts when an object is detected.
- **Arduino Board**: Runs the code and controls the components.

## How It Works
1. **Distance Measurement**:
   - The ultrasonic sensor sends out sound waves and measures the time it takes for the echo to return.
   - The distance is calculated using the formula:  
     `distance = duration / 58.0` (in cm).

2. **Object Detection**:
   - If an object is detected within the threshold distance (50 cm), the system considers it as "object detected."

3. **Gate Control**:
   - When an object is detected:
     - The servo motor rotates to open the gate (90°).
     - The red LED turns off, and the blue LED turns on.
     - The buzzer is activated.
   - If no object is detected for 5 seconds:
     - The servo motor rotates to close the gate (0°).
     - The red LED turns on, and the blue LED turns off.
     - The buzzer is deactivated.

4. **LED and Buzzer States**:
   - **Red LED**: ON when the gate is closed.
   - **Blue LED**: ON when the gate is open.
   - **Buzzer**: ON when an object is detected.

## Pin Configuration
| Component         | Arduino Pin |
|--------------------|-------------|
| Trigger (Ultrasonic) | 2           |
| Echo (Ultrasonic)    | 3           |
| Red LED Anode        | 4           |
| Red LED Cathode      | 8           |
| Blue LED Anode       | 5           |
| Blue LED Cathode     | 7           |
| Servo Motor          | 6           |
| Buzzer               | 12          |

## Constants
- **Threshold Distance**: 50 cm (distance to detect objects).
- **Servo Angles**:
  - Closed: 0°
  - Open: 90°
- **Close Delay**: 5 seconds (time to wait before closing the gate after no object is detected).

## Setup
1. Connect the components to the Arduino as per the pin configuration.
2. Upload the code to the Arduino using the Arduino IDE.
3. Power the Arduino and observe the system in action.

## Code Overview
- **`setup()`**: Initializes pins, sets initial states, and positions the servo motor to the closed position.
- **`getDistance()`**: Measures and returns the distance using the ultrasonic sensor.
- **`loop()`**: Continuously checks for object detection and controls the gate, LEDs, and buzzer based on the detection status.

## Notes
- Ensure the servo motor is properly powered to handle the load.
- Adjust the `thresholdDistance` and `closeDelay` constants as needed for your specific use case.
- Use a stable power supply for consistent performance.

Enjoy building your automated gate control system!