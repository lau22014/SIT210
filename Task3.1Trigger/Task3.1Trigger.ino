#include <Wire.h>
#include <BH1750.h>
#include <WiFiNINA.h>

// WiFi credentials
char ssid[] = "NOKIA-3231-5GHZ";
char pass[] = "EmmaSev@205";

// IFTTT settings
String host = "maker.ifttt.com";
String event = "light_on";
String key = "bxsWTWt-mn_EFcACyVvP12GNlbjwGb1F-qzsmpsuk02";

WiFiClient client;
BH1750 lightMeter;

float threshold = 300.0;
bool isLight = false;

void setup() {
  Serial.begin(9600);
  Wire.begin();
  lightMeter.begin();

  connectWiFi();
}

void loop() {
  // Reconnect if WiFi dropped
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }

  float lux = lightMeter.readLightLevel();

  // Skip if sensor returns error
  if (lux < 0) {
    Serial.println("Sensor error");
    delay(2000);
    return;
  }

  checkLight(lux);

  delay(2000);
}

void connectWiFi() {
  Serial.print("Connecting to WiFi");

  while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    Serial.print(".");
    delay(1000);
  }

  Serial.println("\nConnected!");
}

void checkLight(float lux) {
  if (lux > threshold && !isLight) {
    sendIFTTT(lux, "SUNLIGHT");
    isLight = true;
  }

  if (lux <= threshold && isLight) {
    sendIFTTT(lux, "DARK");
    isLight = false;
  }
}

void sendIFTTT(float lux, String status) {
  if (client.connect(host.c_str(), 80)) {

    String json = "{";
    json += "\"value1\":\"" + String(lux) + "\",";
    json += "\"value2\":\"" + status + "\"";
    json += "}";

    client.println("POST /trigger/" + event + "/with/key/" + key + " HTTP/1.1");
    client.println("Host: " + host);
    client.println("Content-Type: application/json");
    client.print("Content-Length: ");
    client.println(json.length());
    client.println();
    client.println(json);

    Serial.println("Notification sent");
  } else {
    Serial.println("Connection failed");
  }

  // Always close connection after request
  client.stop();
}