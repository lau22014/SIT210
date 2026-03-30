#include <Wire.h>
#include <BH1750.h>

BH1750 lightMeter;

#define PIR_PIN 2
#define SWITCH_PIN 3
#define LED1 5
#define LED2 6

volatile bool motionFlag = false;
volatile bool switchChanged = false;

bool switchState = HIGH;   // INPUT_PULLUP → default HIGH
float lux = 0;
float threshold = 100;

// interrupt: motion detected
void PIR_ISR() {
  motionFlag = true;
}

// interrupt: switch toggled
void SWITCH_ISR() {
  switchChanged = true;
}

// handle manual switch (priority)
void handleSwitch() {
  if (switchChanged) {
    switchState = digitalRead(SWITCH_PIN);
    switchChanged = false;
    if (switchState == LOW) {
      Serial.println("MANUAL MODE: Switch activated → Lights ON");
    }
  }

  // LOW = ON (because pull-up)
  if (switchState == LOW) {
    turnOnLights();
  }
}


void turnOnLights() {
  digitalWrite(LED1, HIGH);
  digitalWrite(LED2, HIGH);
}

void turnOffLights() {
  digitalWrite(LED1, LOW);
  digitalWrite(LED2, LOW);
}

// handle automatic mode
void handleAutoMode() {
  if (switchState == HIGH) { // only when switch OFF

    lux = lightMeter.readLightLevel();

    if (lux < 0) {
      Serial.println("Error: BH1750 value < 0");
      return;
    }

    if (motionFlag && lux < threshold) {
      turnOnLights();
      Serial.println("Motion Detected + environment is Dark → Lights ON for 3 seconds");
      delay(3000);
    } else {
      if (motionFlag) {
        Serial.println("Motion Detected but environment is Bright → Lights OFF");
      }
      turnOffLights();
    }

    motionFlag = false;
  }
}

void setup() {
  Serial.begin(9600);

  pinMode(PIR_PIN, INPUT);
  pinMode(SWITCH_PIN, INPUT_PULLUP);
  pinMode(LED1, OUTPUT);
  pinMode(LED2, OUTPUT);

  Wire.begin();
  lightMeter.begin();

  attachInterrupt(digitalPinToInterrupt(PIR_PIN), PIR_ISR, RISING);
  attachInterrupt(digitalPinToInterrupt(SWITCH_PIN), SWITCH_ISR, CHANGE);
}

void loop() {
  handleSwitch();
  handleAutoMode();
}