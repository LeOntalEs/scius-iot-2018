int pin[] = {16, 5, 4, 0, 2, 14, 12, 13, 15};

//===================================
int ID = 0;
//===================================
const char *ssid = "ois";
const char *password = "ilovestudy";
//===================================
String serverAddress = "192.168.1.4:5000";
//===================================

// MARK : Wifi
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
ESP8266WebServer server(80);
#include <ESP8266HTTPClient.h>

// MARK : OTA
#include <ESP8266mDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>

// MARK : Neopixel LED
#include <Adafruit_NeoPixel.h>
Adafruit_NeoPixel pixels = Adafruit_NeoPixel(1, pin[5], NEO_GRB + NEO_KHZ800);
void led(int r, int g, int b) {
  pixels.setPixelColor(0, pixels.Color(r, g, b));
  pixels.show();
}

// MARK : DHT
#include "DHT.h"
#define DHTPIN pin[6]
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);
bool dhtEnable = false;
int temp = -1;//int(dht.readTemperature());
int humi = -1;//int(dht.readHumidity());

void setup() {
  // MARK : Motor
  pinMode(pin[1], OUTPUT);
  pinMode(pin[2], OUTPUT);
  pinMode(pin[3], OUTPUT);
  pinMode(pin[4], OUTPUT);

  // MARK : Wifi
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  // MARK : Neopixel LED
  pixels.begin();

  // MARK : DHT
  dht.begin();

  Serial.begin(115200);
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  // MARK : OTA
  ArduinoOTA.setHostname("SCiUS");
  ArduinoOTA.onStart([]() {
    String type;
    if (ArduinoOTA.getCommand() == U_FLASH)
      type = "sketch";
    else // U_SPIFFS
      type = "filesystem";

    // NOTE: if updating SPIFFS this would be the place to unmount SPIFFS using SPIFFS.end()
    Serial.println("Start updating " + type);
  });
  ArduinoOTA.onEnd([]() {
    Serial.println("\nEnd");
  });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
  });
  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
    else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
    else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
    else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
    else if (error == OTA_END_ERROR) Serial.println("End Failed");
  });
  ArduinoOTA.begin();
  
}

void loop() {
  ArduinoOTA.handle();

  if(dhtEnable){
    temp = int(dht.readTemperature());
    humi = int(dht.readHumidity());
  }
  
  Serial.println("[HTTP] Request...");

  //String url = "http://192.168.1.3:5000/?temp="+String(temp)+"&humi="+String(humi);
  String url = "http://" + serverAddress + "/getcmd/" + String(ID) + "/" + String(temp) + "/" + String(humi) + "/";

  HTTPClient http;
  http.begin(url);
  int httpCode = http.GET();
  Serial.printf("[HTTP] GET... code: %d\n", httpCode);
  if (httpCode > 0) {
    if (httpCode == HTTP_CODE_OK) {
      String raw = http.getString(); // MOTOR 000 000 000 000 LED 000 000 000 SOUND 0000 0
      Serial.println("[DATA] " + raw);
      int m0 = raw.substring(0, 3).toInt();
      int m1 = raw.substring(3, 6).toInt();
      int m2 = raw.substring(6, 9).toInt();
      int m3 = raw.substring(9, 12).toInt();
      int ledR = raw.substring(12, 15).toInt();
      int ledG = raw.substring(15, 18).toInt();
      int ledB = raw.substring(18, 21).toInt();
      led(ledR, ledG, ledB);

      analogWrite(pin[4], m0);
      analogWrite(pin[3], m1);
      analogWrite(pin[2], m2);
      analogWrite(pin[1], m3);

      int melody = raw.substring(21, 25).toInt();
      int noteDuration = raw.substring(25, 26).toInt();
      if (melody != 0) {
        tone(pin[7], melody, (1000 / noteDuration));
        int pauseBetweenNotes = (1000 / noteDuration); // * 1.30;
        delay(pauseBetweenNotes);
        noTone(pin[7]);
      }

      dhtEnable = raw.substring(26, 27).toInt();
      
    }
  } else {
    Serial.printf("[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
  }
  http.end();

  delay(100);
}

