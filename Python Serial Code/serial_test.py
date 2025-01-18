import serial
import time
import struct

# Replace 'COM3' with the correct port for your Arduino (e.g., '/dev/ttyUSB0' for Linux/Mac)
arduino_port = 'COM3'
baud_rate = 115200  # Must match the Arduino's Serial.begin(baud_rate)

# Open the serial connection
try:
    arduino = serial.Serial(port=arduino_port, baudrate=baud_rate, timeout=1)
    print(f"Connected to Arduino on {arduino_port}")
    time.sleep(2)  # Allow Arduino to initialize
except serial.SerialException as e:
    print(f"Error connecting to Arduino: {e}")
    exit()

def send_data(input1, input2):
    """Send data to the Arduino."""
    data1 = float(input1)
    data2 = float(input2)
    
    packed_data = struct.pack('ff', data1, data2)
    arduino.write(packed_data)  # Encode the string into bytes
    print(f"Sent: {data1}, {data2}")

def receive_data():
    """Receive data from the Arduino."""
    
    if arduino.in_waiting > 0:  # Check if there's data to read
        received_data = arduino.read(8)
        """size of float is 4 bytes"""
        
        return struct.unpack('ff', received_data)  # Read and decode the data
    return None

# Example of bidirectional communication
try:
    while True:
        # Send data to Arduino
        user_input1 = input("Enter the x coordinate/first command (or 'exit' to quit): ")
        if user_input1.lower() == 'exit':
            break

        user_input2 = input("Enter the y coordinate/second command (or 'exit' to quit): ")
        if user_input2.lower() == 'exit':
            break
        print(user_input1)
        print(user_input2)
        send_data(user_input1, user_input2)

        
        
        # Wait and receive response
        time.sleep(1)
        response = receive_data()
        if response:
            print(f"Received from Arduino: {response}")
        
        # Pause before next iteration
        time.sleep(2)

except KeyboardInterrupt:
    print("Exiting program.")
    arduino.close()
