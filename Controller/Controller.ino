#include <AccelStepper.h>
#include <Servo.h>

/****************** VARIABLES ******************/
// Constants (TO BE TWEAKED WHEN BUILT)
#define WRITE_MODE 1
#define TRAVEL_MODE 0
#define STEPPER_MAX_SPEED 1000.0 // 1000.0 if no micro steps
#define STEPPER_WRITE_SPEED 200.0 // 200.0 if no micro steps
#define STEPPER_TRAVEL_SPEED 600.0 // 600.0 if no micro steps
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
unsigned float currX;
unsigned float currY;

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
 * /brief Goes to the (x, y) coordinates given
 */
void goTo(float x, float y) {

}

/****************** RUNTIME ******************/

void setup() {
  // Set the starting mode
  mode = TRAVEL_MODE;

  // Set stepper params
  stepperX.setMaxSpeed(STEPPER_MAX_SPEED);
  stepperX.setSpeed(STEPPER_TRAVEL_SPEED);
  stepperY.setMaxSpeed(STEPPER_MAX_SPEED);
  stepperY.setSpeed(STEPPER_TRAVEL_SPEED);

  // Set up servo params
  writingServo.attach(servoPin);
}

void loop() {
  // Run tests
  stepperX.runSpeed();
  stepperY.runSpeed();
  up(writingServo);
}
