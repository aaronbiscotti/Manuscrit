#include <AccelStepper.h>
#include <Servo.h>

// Note: 200 steps is a full rotation

/****************** VARIABLES ******************/
// Constants (TO BE TWEAKED WHEN BUILT)
#define WRITE_MODE 0
#define TRAVEL_MODE 1
#define CALIBRATE_MODE 2
#define STEPS_TO_CM 1.0 // CHANGE THIS TO HAVE steps * STEPS_TO_CM = cm
#define CM_TO_STEPS 1.0 // CHANGE THIS TO HAVE cm * CM_TO_STEPS = steps
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

// Declare variables
float input1 = 0.0;
float input2 = 0.0;
const int fBufSize = 2 * sizeof(float);

// Mode: 0 if travelling, 1 if writing
char mode;

// Declare Stepper Motor(s)
AccelStepper stepperX(AccelStepper::DRIVER, stepXPin, dirXPin);
AccelStepper stepperY(AccelStepper::DRIVER, stepYPin, dirYPin);

// Declare Servo Motor(s)
Servo writingServo;


/****************** FUNCTIONS ******************/

/**
 * /brief Takes steps and converts it to cms
 *
 * /param steps Number of steps
 * /return Converted cms
 */
float stepsToCms(long steps) {
  return float(steps) * STEPS_TO_CM;
}

/**
 * /brief Takes cms and converts it to steps
 *
 * /param cms Number of cms
 * /return Converted steps
 */
long cmsToSteps(float cms) {
  return long(cms * CM_TO_STEPS);
}

/**
 * /brief Puts the writing servo in the writing (down) position and sets the steppers to write speed
 */
void writeMode() {
  mode = WRITE_MODE;

  // Set writing speed
  stepperX.setMaxSpeed(STEPPER_WRITE_SPEED);
  stepperY.setMaxSpeed(STEPPER_WRITE_SPEED);

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
  stepperX.setMaxSpeed(STEPPER_TRAVEL_SPEED);
  stepperY.setMaxSpeed(STEPPER_TRAVEL_SPEED);

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
  stepperX.setMaxSpeed(STEPPER_CALIBRATE_SPEED + 1);
  stepperY.setMaxSpeed(STEPPER_CALIBRATE_SPEED + 1);
  stepperX.setSpeed(STEPPER_CALIBRATE_SPEED);
  stepperY.setSpeed(STEPPER_CALIBRATE_SPEED);

  // Put into writing position
  writingServo.write(SERVO_UP);

  // Get x == 0.0 first
  // While is no connection between for the head and x axis
  while(false) { // TODO: Change this to detect
    stepperX.runSpeed();
  }
  stepperX.stop();
  stepperX.setCurrentPosition(0);

  // Get y == 0.0 second
  // While is no connection between the head and y axis
  while(false) { // TODO: Change this to detect
    stepperY.runSpeed();
  }
  stepperY.stop();
  stepperY.setCurrentPosition(0);

  return;
}

/**
 * /brief Goes to the (x, y) coordinates given
 *
 * /param x The x coordinate we want to go to, in cm
 * /param y The y coordinate we want to go to, in cm
 */
void goTo(float x, float y) {
  // Convert to steps
  long xSteps = cmsToSteps(x);
  long ySteps = cmsToSteps(y);

  // Use as position targets
  stepperX.moveTo(xSteps);
  stepperY.moveTo(ySteps);

  // Find angle
  double angle;
  if(xSteps - stepperX.currentPosition() == 0) {
    angle = PI / 2;
  } else {
    angle = atan2((ySteps - stepperY.currentPosition()), (xSteps - stepperX.currentPosition()));
  }

  // Find the speeds of both motors
  float currSpeed;
  if(mode == WRITE_MODE) {
    currSpeed = STEPPER_WRITE_SPEED;
  } else { // Otherwise, travel mode
    currSpeed = STEPPER_TRAVEL_SPEED;
  }
  stepperX.setSpeed(float(cos(angle) * currSpeed));
  stepperY.setSpeed(float(sin(angle) * currSpeed));

  // Move there!
  while (stepperX.distanceToGo() != 0 || stepperY.distanceToGo() != 0) {
    if (stepperX.distanceToGo() != 0) {
      stepperX.runSpeed();
    }
    if (stepperY.distanceToGo() != 0) {
      stepperY.runSpeed();
    }
  }

  return;
}

/****************** RUNTIME ******************/

void setup() {
  Serial.begin(115200);

  // Set up servo params
  writingServo.attach(servoPin);

  // Calibrate the device on startup
  calibrate();

  // Set the starting mode
  travelMode();

}

void loop() {
  // Run tests
  // goTo(0.0, 200.0);
  // goTo(200.0, 200.0);
  // goTo(400.0, 0.0);
  // goTo(0.0, 0.0);
  // delay(1000);
  // goTo(1000.0, 7.0);
  // goTo(4000.0, 11.3);
  // goTo(10000.0, 200.0);
  // goTo(0.0, 0.0);
  // delay(10000);

  // Wait for the next command
  if (Serial.available() >= fBufSize) {  // Wait until at least 2 floats are available
    // Read the incoming data
    byte buffer[fBufSize];
    Serial.readBytes(buffer, fBufSize);

    memcpy(&input1, buffer, sizeof(float));
    memcpy(&input2, buffer + sizeof(float), sizeof(float));
      
    // Print the received data to Serial Monitor
    Serial.write((byte*)&input1, sizeof(float));
    Serial.write((byte*)&input2, sizeof(float));
  }
}
