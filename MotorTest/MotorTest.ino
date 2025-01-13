#include <AccelStepper.h>

// Declare pins
const int stepXPin = 2;
const int dirXPin = 5;
const int stepYPin = 3;
const int dirYPin = 6;

// Declare Stepper Motor(s)
AccelStepper stepperX(AccelStepper::DRIVER, stepXPin, dirXPin);
AccelStepper stepperY(AccelStepper::DRIVER, stepYPin, dirYPin);

void setup() {
  // Set stepper params
  stepperX.setMaxSpeed(1000.0);
  stepperX.setSpeed(200.0);
  //stepperX.setAcceleration(1000.0);
  //stepperX.moveTo(1000);
  stepperY.setMaxSpeed(1000.0);
  stepperY.setSpeed(100.0);
  //stepperY.setAcceleration(1000.0);
  //stepperY.moveTo(1000);
}

void loop() {
  // Run tests

  stepperX.runSpeed();
  stepperY.runSpeed();

  /*
  if(!stepperX.runSpeed()) {
    stepperX.moveTo(-stepperX.currentPosition());
  }

  if(!stepperY.runSpeed()) {
    stepperY.moveTo(-stepperY.currentPosition());
  }
  */
}
