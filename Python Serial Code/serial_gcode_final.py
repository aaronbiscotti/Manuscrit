import serial
import time
import struct
import queue
import sys
import os

# Remember, integers are longs in python

arduino_port = 'COM6'
baud_rate = 115200
steps_to_cm = 1600
cm_to_steps = 1 / steps_to_cm

# Open the serial connection
try:
    arduino = serial.Serial(port=arduino_port, baudrate=baud_rate, timeout=1)
    print(f"Connected to Arduino on {arduino_port}")
    time.sleep(2)  # Allow Arduino to initialize
except serial.SerialException as e:
    print(f"Error connecting to Arduino: {e}")
    exit()

### DATA SENDING ###

def send_data(input1, input2):
    """Send data to the Arduino."""
    data1 = input1
    data2 = input2
    
    packed_data = struct.pack('ll', data1, data2)
    arduino.write(packed_data)  # Encode the string into bytes
    print(f"Sent: {data1}, {data2}")

def receive_data():
    """Receive data from the Arduino."""
    
    while arduino.in_waiting == 0:  # Check if there's data to read
        continue

    received_data = arduino.read(8)
    """size of long is 4 bytes"""
    ret = struct.unpack('ll', received_data)  # Read and decode the data
    return ret 

### FILE PROCESSING ###

def gcode_to_steps(gcode_coordinate):
    return int(gcode_coordinate * 200) #TODO: CHANGE CONSTANT

def process_gcode_file(file_path, job_num):
    """
    Processes a gcode file line by line, converts to custom language, and stores the result in a queue.

    :param file_path: Path to the .txt file
    :param job_num: The job number
    :return: A queue containing processed data
    """
    # Create a queue to store processed results
    processed_queue = queue.Queue()

    try:
        with open(file_path, 'r') as file:
            processed_queue.put([-1, -job_num])
            processed_queue.put([-1, 1])
            writing = False

            for line in file:
                # Strip line
                line = line.strip()
                if not line:
                    continue

                # Parse line (assumes "G<type> X<value> Y<value>")
                parts = line.split()
                if len(parts) < 3:
                    print(f"Skipping bad line: {line}")
                    continue
                g_value = int(parts[0][1:])
                x_value = gcode_to_steps(int(parts[1][1:]))
                y_value = abs(gcode_to_steps(int(parts[2][1:]))) # REFLECT OVER THE AXIS

                # Change writing mode check
                if g_value == 0: # travel mode
                    if writing:
                        processed_queue.put([-1, 1]) # Travel mode command
                        writing = False
                elif g_value == 1: # write mode
                    if not writing:
                        processed_queue.put([-1, 0]) # Writing mode command
                        writing = True
                else:
                    print(f"Error: g value is {g_value}")
                    continue

                # Send the coordinates
                while x_value > gcode_to_steps(150): # Limits
                    x_value = x_value // 10
                while y_value > gcode_to_steps(150): # Limits
                    y_value = y_value // 10
                processed_queue.put([x_value, y_value])
            
            # Clarify the end of the job
            processed_queue.put([-1, -job_num])
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred while processing the file: {e}")

    return processed_queue

### RUNTIME ###

# Bidirectional communication
try:
    job = 1
    while True:
        # Process the gcode file
        Q = process_gcode_file(input("Enter gcode file: "), 1)

        # Send data to Arduino
        while not Q.empty():
            instruction = Q.get()
            user_input1 = instruction[0]
            user_input2 = instruction[1]
            
            # FOR TESTING
            print(user_input1)
            print(user_input2)
            
            # Send the data
            send_data(user_input1, user_input2)

            # Wait and receive response
            response = receive_data()
            if response:
                print(f"Received from Arduino: {response}")
            
        # Pause before next iteration
        time.sleep(2)

except KeyboardInterrupt:
    print("Exiting program.")
    arduino.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # If file path provided as argument, process it
        Q = process_gcode_file(sys.argv[1], 1)
        while not Q.empty():
            instruction = Q.get()
            user_input1 = instruction[0]
            user_input2 = instruction[1]
            
            # FOR TESTING
            print(user_input1)
            print(user_input2)
            
            # Send the data
            send_data(user_input1, user_input2)
            response = receive_data()
            if response:
                print(f"Received from Arduino: {response}")
            
        time.sleep(2)
        arduino.close()
        sys.exit(0)