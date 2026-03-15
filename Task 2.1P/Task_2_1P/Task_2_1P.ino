#include <WiFiNINA.h>
#include <ThingSpeak.h>
#include <DHT.h>

// DHT sensor setup
#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// Light sensor pin
#define LIGHTPIN A0

// WiFi credentials
char ssid[] = "NOKIA-3231-5GHZ";
char pass[] = "EmmaSev@205";

// ThingSpeak settings
unsigned long myChannelNumber = 3300774;
const char* myWriteAPIKey = "SSW6M5GJTV3O65J2";

WiFiClient client;

void connectWiFi();
void sendToThingSpeak(float temp, int light);

void setup() {
  Serial.begin(9600);
  dht.begin();

  connectWiFi();
  ThingSpeak.begin(client);
}

void loop() {

  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }

  float temperature = dht.readTemperature();
  int lightLevel = analogRead(LIGHTPIN);

  Serial.print("Light: ");
  Serial.println(lightLevel);

  Serial.print("Temperature: ");
  Serial.println(temperature);

  if (isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor");
    return;
  }

  sendToThingSpeak(temperature, lightLevel);

  delay(30000);
}

void connectWiFi() {
  while(WiFi.status() != WL_CONNECTED){
    WiFi.begin(ssid, pass);
    Serial.print(".");
    delay(5000);
  }
  Serial.println("\nConnected.");
}

void sendToThingSpeak(float temp, int light) {

  ThingSpeak.setField(1, temp);
  ThingSpeak.setField(2, light);

  int status = ThingSpeak.writeFields(myChannelNumber, myWriteAPIKey);

  if (status == 200) {
    Serial.println("Data sent to ThingSpeak");
  } else {
    Serial.println("Failed to send data");
  }
}