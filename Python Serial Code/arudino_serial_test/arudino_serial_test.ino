// This file is for testing the serial sending works

/****************** VARIABLES ******************/

// Declare variables
float input1 = 0.0;
float input2 = 0.0;
const int fBufSize = 2 * sizeof(float);


/****************** RUNTIME ******************/

void setup() {
  Serial.begin(115200);
}

void loop() {
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
