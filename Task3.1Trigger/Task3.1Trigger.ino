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

// Hysteresis thresholds to avoid rapid toggling
float thresholdHigh = 320.0; // upper bound for SUNLIGHT
float thresholdLow = 280.0;  // lower bound for DARK

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

// Check light state using hysteresis to prevent flapping
void checkLight(float lux) {

  // Switch to SUNLIGHT only when exceeding upper threshold
  if (lux > thresholdHigh && !isLight) {
    sendIFTTT(lux, "SUNLIGHT", thresholdHigh);
    isLight = true;
  }

  // Switch to DARK only when dropping below lower threshold
  if (lux < thresholdLow && isLight) {
    sendIFTTT(lux, "DARK", thresholdLow);
    isLight = false;
  }
}

// Send data to IFTTT
void sendIFTTT(float lux, String status, float thresholdValue) {
  if (client.connect(host.c_str(), 80)) {

    String json = "{";
    json += "\"value1\":\"" + String(lux) + "\",";
    json += "\"value2\":\"" + status + "\",";
    json += "\"value3\":\"" + String(thresholdValue) + "\"";
    json += "}";

    client.println("POST /trigger/" + event + "/with/key/" + key + " HTTP/1.1");
    client.println("Host: " + host);
    client.println("Content-Type: application/json");
    client.print("Content-Length: ");
    client.println(json.length());
    client.println();
    client.println(json);

    delay(500); // wait server response
    client.stop(); 
    Serial.println("Notification sent: " + status);
  } else {
    Serial.println("Connection failed");
  }
}