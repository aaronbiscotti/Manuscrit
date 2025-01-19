import serial
import time
import struct

# Remember, integers are longs in python

arduino_port = 'COM3'
baud_rate = 115200
steps_to_cm = 1600
cm_to_steps = 1 / steps_to_cm

try:
    arduino = serial.Serial(port=arduino_port, baudrate=baud_rate, timeout=1)
    print(f"Connected to Arduino on {arduino_port}")
except serial.SerialException as e:
    print(f"Error connecting to Arduino: {e}")
    exit()

def send_data(input1, input2):
    """Send data to the Arduino."""
    data1 = gcode_to_steps(input1)
    data2 = gcode_to_steps(input2)
    
    packed_data = struct.pack('ll', data1, data2)
    arduino.write(packed_data)  # Encode the string into bytes
    print(f"Sent: {data1}, {data2}")

def receive_data():
    """Receive data from the Arduino."""
    
    if arduino.in_waiting > 0:  # Check if there's data to read
        received_data = arduino.read(8)
        """size of long is 4 bytes"""
        
        return struct.unpack('ll', received_data)  # Read and decode the data
    return None

def gcode_to_steps(gcode_coordinate):
    return int(gcode_coordinate * 1) #TODO: CHANGE CONSTANT

try:
    while True:
        # Send data to Arduino
        user_input1 = input("Enter the x coordinate/first command: ")
        if user_input1.lower() == 'exit':
            break

        user_input2 = input("Enter the y coordinate/second command: ")
        if user_input2.lower() == 'exit':
            break
        print(user_input1)
        print(user_input2)
        send_data(user_input1, user_input2)

        
        # Wait and receive response
        response = receive_data()
        if response:
            print(f"Received from Arduino: {response}")

except KeyboardInterrupt:
    print("Exiting program.")
    arduino.close()
