#include <SoftwareSerial.h>
#include <TinyGPS.h>
#include <SPI.h>
#include <LoRa.h>
#include <U8x8lib.h>
#include <U8g2lib.h>

#define sss 18
#define rst 14
#define dio0 26

U8X8_SSD1306_128X64_NONAME_SW_I2C u8x8(15, 4, 16);


TinyGPS gps;
SoftwareSerial ss(16, 17);  // RX, TX

void setup()
{
  u8x8.begin();
  u8x8.setFont(u8x8_font_chroma48medium8_r);
  u8x8.drawString(0, 1, "LoRa Tx");
  
  Serial.begin(9600);
  ss.begin(9600);

  Serial.println("LoRa Sender");
  SPI.begin(5, 19, 27, 18);
  LoRa.setPins(sss, rst, dio0);
  
  if (!LoRa.begin(915E6)) {
    Serial.println("Start of LoRa failed!");
    while (1);
  }
}

void loop()
{
  bool newData = false;
  unsigned long chars;
  unsigned short sentences, failed;

  // For one second we parse GPS data and report some key values
  for (unsigned long start = millis(); millis() - start < 2000;)
  {
    while (ss.available())
    {
      char c = ss.read();
//        Serial.write(c); // uncomment this line if you want to see the GPS data flowing
      if (gps.encode(c)) // Did a new valid sentence come in?
        newData = true;
    }
  }
  
  if (newData)
  {
    float flat, flon;
    unsigned long age;
    gps.f_get_position(&flat, &flon, &age);
    Serial.print(" LAT=");
    Serial.print(flat == TinyGPS::GPS_INVALID_F_ANGLE ? 0.0 : flat, 6);
    Serial.print(" LON=");
    Serial.print(flon == TinyGPS::GPS_INVALID_F_ANGLE ? 0.0 : flon, 6);
    Serial.print(" ALT: ");
    Serial.print(gps.f_altitude() == TinyGPS::GPS_INVALID_F_ALTITUDE ? 0 : gps.f_altitude());
    Serial.print(" SAT=");
    Serial.print(gps.satellites() == TinyGPS::GPS_INVALID_SATELLITES ? 0 : gps.satellites());
    Serial.print(" PREC=");
    Serial.print(gps.hdop() == TinyGPS::GPS_INVALID_HDOP ? 0 : gps.hdop());

    // send packet (lat, lng, alt, sat)
    LoRa.beginPacket();
    LoRa.print(flat == TinyGPS::GPS_INVALID_F_ANGLE ? 0.0 : flat, 6);
    LoRa.print(":");
    LoRa.print(flon == TinyGPS::GPS_INVALID_F_ANGLE ? 0.0 : flon, 6);
    LoRa.print(":");
    LoRa.print(gps.f_altitude());
    LoRa.print(":");
    LoRa.print(gps.satellites());
    LoRa.endPacket();
  }
  
  gps.stats(&chars, &sentences, &failed);
  Serial.print(" CHARS=");
  Serial.print(chars);
  Serial.print(" SENTENCES=");
  Serial.print(sentences);
  Serial.print(" CSUM ERR=");
  Serial.println(failed);
  if (chars == 0)
    Serial.println("** No characters received from GPS: check wiring **");
}
