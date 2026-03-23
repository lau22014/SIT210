#include <WiFiNINA.h>
#include <ArduinoMqttClient.h>

// WiFi
char ssid[] = "NOKIA-3231-5GHZ";
char pass[] = "EmmaSev@205";

// MQTT
const char broker[] = "broker.emqx.io";
const int port = 1883;

const char* topicWave = "ES/Wave";
const char* topicPat = "ES/Pat";

// LED
const int HALLWAY_LED = 4;
const int BATHROOM_LED = 5;

// Objects
WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

void setup() {
  Serial.begin(9600);

  pinMode(HALLWAY_LED, OUTPUT);
  pinMode(BATHROOM_LED, OUTPUT);

  connectWiFi();
  connectMQTT();

  // Subscribe topics
  mqttClient.subscribe(topicWave, 1);
  mqttClient.subscribe(topicPat, 1);

  Serial.println("Subscribed to topics");
}

void loop() {
  mqttClient.poll();
  handleMessage(); 
}

// Handle incoming MQTT messages
void handleMessage() {
  int messageSize = mqttClient.parseMessage();

  // if no message is received, exit the function
  if (!messageSize) return;

  String topic = mqttClient.messageTopic();
  String message = readMessage();

  Serial.print("Message: ");
  Serial.println(message);

  // if Wave message → turn ON LEDs
  if (topic == topicWave) {

    turnOnLEDs();
  } 
  // if Pat message → turn OFF LEDs
  else if (topic == topicPat) {
    turnOffLEDs();
  }
}

// Read full payload from MQTT buffer
String readMessage() {
  String msg = "";

  while (mqttClient.available()) {
    msg += (char)mqttClient.read();
  }

  return msg;
}

// LED control functions
void turnOnLEDs() {
  Serial.println("Wave → LED ON");
  digitalWrite(HALLWAY_LED, HIGH);
  digitalWrite(BATHROOM_LED, HIGH);
}

void turnOffLEDs() {
  Serial.println("Pat → LED OFF");
  digitalWrite(HALLWAY_LED, LOW);
  digitalWrite(BATHROOM_LED, LOW);
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