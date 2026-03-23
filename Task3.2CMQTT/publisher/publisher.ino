#include <WiFiNINA.h>
#include <ArduinoMqttClient.h>
#include <HCSR04.h>

// WiFi 
char ssid[] = "NOKIA-3231-5GHZ";
char pass[] = "EmmaSev@205";

// MQTT 
const char broker[] = "broker.emqx.io";
const int port = 1883;

const char* topicWave = "ES/Wave";
const char* topicPat  = "ES/Pat";
const char* myName    = "Chun Hong Lau"; 

// Ultrasonic 
const int TRIG_PIN = 7;   // cm
const int ECHO_PIN = 6;  // ms
UltraSonicDistanceSensor hc(TRIG_PIN, ECHO_PIN);

// Threshold
const int DIST_THRESHOLD = 20;   // cm
const int TIME_THRESHOLD = 500;  // ms

// Objects
WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

// Variables 
int prevDistance = 100;
unsigned long startTime = 0;

void setup() {
  Serial.begin(9600);

  connectWiFi();
  connectMQTT();
}

void loop() {
  mqttClient.poll();

  // get distance from sensor
  float distance = hc.measureDistanceCm();
  // skip when the sensor has an issue
  if (distance < 0) return;
  handleGesture(distance);

  delay(100);
}

void handleGesture(float distance) {
  Serial.print("Distance: ");
  Serial.println(distance);

  // Detect hand entering
  if (distance < DIST_THRESHOLD && prevDistance >= DIST_THRESHOLD) {
    startTime = millis();
  }

  // Detect hand leaving
  if (distance >= DIST_THRESHOLD && prevDistance < DIST_THRESHOLD) {
    unsigned long duration = millis() - startTime;

    if (duration < TIME_THRESHOLD) {
      Serial.println("Wave → publish");
      publishMessage(topicWave);
    } else {
      Serial.println("Pat → publish");
      publishMessage(topicPat);
    }
  }
  prevDistance = distance;
}


void publishMessage(const char* topic) {
  mqttClient.beginMessage(topic);
  mqttClient.print(myName);
  mqttClient.endMessage();
}

void connectWiFi() {
  Serial.print("Connecting WiFi");
  while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println("\nWiFi connected");
}

void connectMQTT() {
  Serial.print("Connecting MQTT");
  while (!mqttClient.connect(broker, port)) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println("\nMQTT connected");
}