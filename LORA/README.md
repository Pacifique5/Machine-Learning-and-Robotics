# LoRa Chat Example

This project demonstrates a simple chat application using LoRa radios with Arduino. It allows two devices to send and receive messages via LoRa, displaying received messages and estimating the distance based on RSSI.

## Hardware Requirements

- Arduino board (Uno, Nano, etc.)
- LoRa module (e.g., HopeRF RFM95)
- Jumper wires

## Wiring

| Arduino Pin | LoRa Pin |
|-------------|----------|
| 8           | NSS/CS   |
| 4           | RST      |
| 7           | DIO0     |
| 11 (MOSI)   | MOSI     |
| 12 (MISO)   | MISO     |
| 13 (SCK)    | SCK      |
| 3.3V        | VCC      |
| GND         | GND      |

## Software Requirements

Install the following Arduino libraries:

- [RadioHead](https://www.airspayce.com/mikem/arduino/RadioHead/)  
  (Install via Arduino Library Manager: **Sketch > Include Library > Manage Libraries...** and search for "RadioHead")

- SPI library (comes pre-installed with Arduino IDE)

## Usage

1. Connect your LoRa module to the Arduino as described above.
2. Open `lora.ino` in the Arduino IDE.
3. Select your board and port.
4. Upload the sketch.
5. Open the Serial Monitor at 115200 baud.
6. Type a message and press Enter to send via LoRa.
7. Received messages will be displayed with RSSI and estimated distance.

## Notes

- Make sure both devices use the same frequency (`RF95_FREQ`).
- Adjust the RSSI-to-distance formula in `estimateDistance()` for your environment.

---
**Main file:** [lora.ino](lora.ino)