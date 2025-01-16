#include <AccelStepper.h>
#include <Servo.h>

/****************** VARIABLES ******************/
// Constants (TO BE TWEAKED WHEN BUILT)
#define WRITE_MODE 0
#define TRAVEL_MODE 1
#define CALIBRATE_MODE 2
#define STEPPER_MAX_SPEED 1000.0 // 1000.0 if no micro steps
#define STEPPER_WRITE_SPEED 200.0 // 200.0 if no micro steps
#define STEPPER_TRAVEL_SPEED 600.0 // 600.0 if no micro steps
#define STEPPER_CALIBRATE_SPEED 100.0 // 100.0 if no micro steps
#define SERVO_UP 160
#define SERVO_DOWN 30

// Declare pins
const int stepXPin = 2;
const int dirXPin = 5;
const int stepYPin = 3;
const int dirYPin = 6;
const int servoPin = 4; // stepZPin

// Mode: 0 if travelling, 1 if writing
char mode;

// Current position variables
float currX;
float currY;

// Declare Stepper Motor(s)
AccelStepper stepperX(AccelStepper::DRIVER, stepXPin, dirXPin);
AccelStepper stepperY(AccelStepper::DRIVER, stepYPin, dirYPin);

// Declare Servo Motor(s)
Servo writingServo;


/****************** FUNCTIONS ******************/

/**
 * /brief Puts the writing servo in the writing (down) position and sets the steppers to write speed
 */
void writeMode() {
  mode = WRITE_MODE;

  // Set writing speed
  stepperX.setSpeed(STEPPER_WRITE_SPEED);
  stepperY.setSpeed(STEPPER_WRITE_SPEED);

  // Put into writing position
  writingServo.write(SERVO_DOWN);

  return;
}

/**
 * /brief Puts the writing servo in the travel (up) position and sets the steppers to travel speed
 */
void travelMode() {
  // Set the mode
  mode = TRAVEL_MODE;

  // Set writing speed
  stepperX.setSpeed(STEPPER_TRAVEL_SPEED);
  stepperY.setSpeed(STEPPER_TRAVEL_SPEED);

  // Put into writing position
  writingServo.write(SERVO_UP);

  return;
}

/**
 * /brief Calibrates the machine by bringing the head to (0, 0)
 */
void calibrate() {
  // Set calibrate mode
  mode = CALIBRATE_MODE;

  // Set calibrate speed
  stepperX.setSpeed(STEPPER_CALIBRATE_SPEED);
  stepperY.setSpeed(STEPPER_CALIBRATE_SPEED);

  // Put into writing position
  writingServo.write(SERVO_UP);

  // Get x == 0.0 first
  // While is no connection between for the head and x axis
  while(false) {
    stepperX.runSpeed();
  }
  stepperX.stop();
  currX = 0.0;

  // Get y == 0.0 second
  // While is no connection between the head and y axis
  while(false) {
    stepperY.runSpeed();
  }
  stepperY.stop();
  currY = 0.0;

  return;
}

/**
 * /brief Goes to the (x, y) coordinates given
 */
void goTo(float x, float y) {

}

/****************** RUNTIME ******************/

void setup() {
  // Set stepper params
  stepperX.setMaxSpeed(STEPPER_MAX_SPEED);
  stepperY.setMaxSpeed(STEPPER_MAX_SPEED);

  // Set up servo params
  writingServo.attach(servoPin);

  // Calibrate the device on startup
  calibrate();

  // Set the starting mode
  travelMode();
}

void loop() {
  // Run tests
  travelMode();
  stepperX.runSpeed();
  stepperY.runSpeed();
}
