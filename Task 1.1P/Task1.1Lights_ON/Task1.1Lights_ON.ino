// --- Pin definitions ---
const int BUTTON_PIN = 2;
const int PORCH_LED_PIN = 3;
const int HALLWAY_LED_PIN = 4;

// --- Time settings (milliseconds) ---
const unsigned long PORCH_DURATION = 30000;
const unsigned long HALLWAY_DURATION = 60000;

// --- Light state variables ---
bool porchIsOn = false;
bool hallwayIsOn = false;

unsigned long porchStartTime = 0;
unsigned long hallwayStartTime = 0;

void setup() {
  initHardware();
  Serial.begin(9600);
}

void loop() {
  checkButton();

  manageLight(PORCH_LED_PIN, porchIsOn, porchStartTime, PORCH_DURATION);
  manageLight(HALLWAY_LED_PIN, hallwayIsOn, hallwayStartTime, HALLWAY_DURATION);
}

// =========================
// MODULE FUNCTIONS
// =========================

// setup pins
void initHardware() {

  pinMode(BUTTON_PIN, INPUT_PULLUP);

  pinMode(PORCH_LED_PIN, OUTPUT);
  pinMode(HALLWAY_LED_PIN, OUTPUT);

  digitalWrite(PORCH_LED_PIN, LOW);
  digitalWrite(HALLWAY_LED_PIN, LOW);
}

// check if button is pressed
void checkButton() {
  if (digitalRead(BUTTON_PIN) == LOW) {
    turnOnLight(PORCH_LED_PIN, porchIsOn, porchStartTime);
    turnOnLight(HALLWAY_LED_PIN, hallwayIsOn, hallwayStartTime);
  }
}

// reusable function to turn on a light
void turnOnLight(int ledPin, bool &lightState, unsigned long &startTime) {

  digitalWrite(ledPin, HIGH);

  lightState = true;
  startTime = millis();
}

// reusable timer manager
void manageLight(int ledPin, bool &lightState, unsigned long &startTime, unsigned long duration) {

  unsigned long currentTime = millis();

  if (lightState && (currentTime - startTime >= duration)) {

    digitalWrite(ledPin, LOW);
    lightState = false;

    Serial.println("Light turned off after timer.");
  }
}