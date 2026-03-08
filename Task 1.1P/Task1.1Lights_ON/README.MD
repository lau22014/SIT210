# Task 1.1 – Switching ON Lights

## System Description

This project simulate a simple smart lighting system for an elderly care home. When Linda comes home at night, she can press a button to turn on the lights so she can see the entrance clearly.

When the button is pressed:

- Porch light (red led) turns on for **30 seconds**
- Hallway light (green led) turns on for **60 seconds**

The system uses an **Arduino Nano 33 IoT**, two LEDs, and a push button.  
The program is written using **modular programming**, where the code is split into smaller functions to make it easier to read and manage.

---

## Program Structure Overview

The program is divided into several functions so the code is easier to understand and maintain.

### setup()

This function run once when the Arduino start.  
It calls `initHardware()` to setup the pins and start the serial monitor.

---

### initHardware()

This function setup the button and LED pins.  
The button use `INPUT_PULLUP` and both LEDs are set as outputs.  
Both lights are also turned off at the beginning.

---

### loop()

The loop() function run continuously.  
It check if the button is pressed using `checkButton()`.

It also calls `manageLight()` for each LED to control how long the lights stay on.

---

### checkButton()

This function read the button input.  
If the button is pressed, it calls `turnOnLight()` for both LEDs.

A small delay is used to reduce button bouncing.  
If the button is pressed again while lights are on, the timer will reset.

---

### turnOnLight()

This function turn on a LED.

It will:

- set the LED HIGH
- update the light state variable
- store the current time using `millis()`

This allow the program to track how long the light stay on.

---

### manageLight()

This function control the timer of each light.

It checks how much time has passed since the light was turned on.  
If the duration is reached, the LED will turn off and the state is updated.

Because this function use parameters, it can be reuse for multiple lights.
