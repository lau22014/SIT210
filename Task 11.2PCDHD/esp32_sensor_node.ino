#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

#define DHT_PIN     4
#define MQ2_PIN     34
#define BUZZER_PIN  27
#define DHT_TYPE    DHT11

const char* WIFI_SSID  = "LAU 5";
const char* WIFI_PASS  = "0983917052";
const char* MQTT_BROKER = "192.168.0.104";   // IP of RPi
const int   MQTT_PORT   = 1883;
const char* MQTT_TOPIC  = "home/kitchen/sensors";

const float TEMP_THRESHOLD  = 50.0;
const int   SMOKE_THRESHOLD = 600;   // MQ-2 ADC raw (0–4095)

DHT dht(DHT_PIN, DHT_TYPE);
WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);

void connectWiFi() {
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    Serial.print("Connecting WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500); Serial.print(".");
    }
    Serial.println("\nConnected: " + WiFi.localIP().toString());
}

void connectMQTT() {
    while (!mqtt.connected()) {
        Serial.print("Connecting MQTT... ");
        if (mqtt.connect("ESP32_KitchenNode")) {
            Serial.println("OK");
        } else {
            Serial.printf("Failed rc=%d, retry in 2s\n", mqtt.state());
            delay(2000);
        }
    }
}

void setup() {
    Serial.begin(115200);
    pinMode(BUZZER_PIN, OUTPUT);
    dht.begin();
    connectWiFi();
    mqtt.setServer(MQTT_BROKER, MQTT_PORT);
    connectMQTT();
}

void loop() {
    if (!mqtt.connected()) connectMQTT();
    mqtt.loop();

    float temp  = dht.readTemperature();
    int   smoke = analogRead(MQ2_PIN);

    if (isnan(temp)) {
        Serial.println("DHT11 read failed, skipping...");
        delay(2000);
        return;
    }

    bool tempHigh  = temp  >= TEMP_THRESHOLD;
    bool smokeHigh = smoke >= SMOKE_THRESHOLD;

    int level = 0;
    if (tempHigh && smokeHigh) level = 2;
    else if (tempHigh || smokeHigh) level = 1;

    // Buzzer local when level 2
    digitalWrite(BUZZER_PIN, level == 2 ? HIGH : LOW);

    // Publish JSON
    StaticJsonDocument<128> doc;
    doc["temp"]  = temp;
    doc["smoke"] = smoke;
    doc["level"] = level;

    char payload[128];
    serializeJson(doc, payload);
    mqtt.publish(MQTT_TOPIC, payload);

    Serial.printf("Temp: %.1f°C | Smoke: %d | Level: %d\n", temp, smoke, level);
    delay(2000);
}
