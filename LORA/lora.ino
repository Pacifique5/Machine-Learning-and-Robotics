#include <SPI.h>
#include <RH_RF95.h>
// Pin definitions
#define RFM95_CS 8
#define RFM95_RST 4
#define RFM95_INT 7
#define RF95_FREQ 951.0
RH_RF95 rf95(RFM95_CS, RFM95_INT);
void setup() {
  pinMode(RFM95_RST, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);
  Serial.begin(115200);
  while (!Serial) delay(1);
  // Manual reset of LoRa module
  digitalWrite(RFM95_RST, LOW);
  delay(10);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);
  if (!rf95.init()) {
    Serial.println("LoRa radio init failed");
    while (1);
  }
  Serial.println("LoRa radio init OK!");
  if (!rf95.setFrequency(RF95_FREQ)) {
    Serial.println("setFrequency failed");
    while (1);
  }
  Serial.print("Set Freq to: ");
  Serial.println(RF95_FREQ);
  rf95.setTxPower(23, false);
  Serial.println("Ready to chat via LoRa!");
}
float estimateDistance(int rssi) {
  // Simple RSSI to distance approximation
  float distance = pow(10, ((-rssi - 40) / 20.0));  // You can tweak -40 and 20.0
  return distance;
}
void loop() {
  // Receive
  if (rf95.available()) {
    uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
    uint8_t len = sizeof(buf);
    if (rf95.recv(buf, &len)) {
      buf[len] = '\0'; // Ensure null-terminated string
      Serial.print("[Friend]: ");
      Serial.println((char*)buf);
      int rssi = rf95.lastRssi();
      float distance = estimateDistance(rssi);
      Serial.print("RSSI: ");
      Serial.println(rssi);
      Serial.print("Estimated distance: ");
      Serial.print(distance, 2);
      Serial.println(" meters");
      Serial.println("***");
    }
  }
  // Send
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    if (input.length() > 0) {
      rf95.send((uint8_t*)input.c_str(), input.length());
      rf95.waitPacketSent();
      Serial.print("[You]: ");
      Serial.println(input);
      Serial.println("***");
    }
  }
}