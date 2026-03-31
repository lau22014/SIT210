#include <Wire.h>
#include <BH1750.h>
#include <WiFiNINA.h>

BH1750 lightMeter;
WiFiClient client;

// WiFi
char ssid[] = "lau";
char pass[] = "12345678";

// IFTTT
String host = "maker.ifttt.com";
String event = "light_on";
String key = "lEIurNjSxb1yeQLJP7HFkQOPabMV41zjye8Z4xwrhaU";

// light status
bool isLight = false;

void setup() {
  Serial.begin(9600);
  Wire.begin();

  lightMeter.begin();

  // connect wifi
  Serial.print("Connecting WiFi...");
  while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println("Connected!");
}

void loop() {

  float lux = lightMeter.readLightLevel();

  Serial.print("Lux: ");
  Serial.println(lux);

  // if bright
  if (lux > 300 && isLight == false) {
    sendIFTTT("SUNLIGHT", lux);
    isLight = true;
  }

  // if dark
  if (lux < 200 && isLight == true) {
    sendIFTTT("DARK", lux);
    isLight = false;
  }

  delay(2000);
}

// send to IFTTT
void sendIFTTT(String status, float lux) {

  if (client.connect(host.c_str(), 80)) {

    String data = "{";
    data += "\"value1\":\"" + String(lux) + "\",";
    data += "\"value2\":\"" + status + "\"";
    data += "}";

    client.println("POST /trigger/" + event + "/with/key/" + key + " HTTP/1.1");
    client.println("Host: " + host);
    client.println("Content-Type: application/json");
    client.print("Content-Length: ");
    client.println(data.length());
    client.println();
    client.println(data);

    Serial.println("Sent to IFTTT: " + status);

    client.stop();
  } else {
    Serial.println("Failed to connect");
  }
}
