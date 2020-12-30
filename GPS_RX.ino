#include <SPI.h>
#include <LoRa.h>
#include <U8x8lib.h>

#define ss 18
#define rst 14
#define dio0 26

U8X8_SSD1306_128X64_NONAME_SW_I2C u8x8(15, 4, 16);

String RxString;
String RxRSSI;

void setup() {
  Serial.begin(9600);
  
  Serial.println("LoRa Rx");
  
  u8x8.begin();
  u8x8.setFont(u8x8_font_chroma48medium8_r);
  u8x8.drawString(0, 1, "LoRa Rx");
  
  SPI.begin(5, 19, 27, 18);
  LoRa.setPins(ss, rst, dio0);
  
  if (!LoRa.begin(915E6)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }
}

void loop() {
  // try to parse packet
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    while (LoRa.available()) {
      RxString = (char)LoRa.read();
      Serial.print(RxString);
    }
    RxRSSI = LoRa.packetRssi();
    Serial.print(":");
    Serial.print(RxRSSI);
    Serial.println();
  }
}
