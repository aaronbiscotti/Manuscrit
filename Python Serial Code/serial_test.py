import serial
import time
import struct
import queue

# Remember, integers are longs in python

arduino_port = 'COM3'
baud_rate = 115200
steps_to_cm = 1600
cm_to_steps = 1 / steps_to_cm

### DATA SENDING ###

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

### FILE PROCESSING ###

def gcode_to_steps(gcode_coordinate):
    return int(gcode_coordinate * 1) #TODO: CHANGE CONSTANT

def process_gcode_file(file_path, job_num):
    """
    Processes a .nc (gcode) file line by line, converts to custom language, and stores the result in a queue.

    :param file_path: Path to the .nc file
    :param job_num: The job number
    :return: A queue containing processed data
    """
    # Create a queue to store processed results
    processed_queue = queue.Queue()

    try:
        with open(file_path, 'r') as file:
            processed_queue.put([-1, -job_num])
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
                g_value = parts[0]
                x_value = int(parts[1][1:])
                y_value = int(parts[2][1:])

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
                processed_queue.put([x_value, y_value])
            
            # Clarify the end of the job
            processed_queue.put([-1, -job_num])
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred while processing the file: {e}")

    # FOR TESTING
    print(processed_queue)

    return processed_queue

### RUNTIME ###

# Open the serial connection
try:
    arduino = serial.Serial(port=arduino_port, baudrate=baud_rate, timeout=1)
    print(f"Connected to Arduino on {arduino_port}")
    time.sleep(2)  # Allow Arduino to initialize
except serial.SerialException as e:
    print(f"Error connecting to Arduino: {e}")
    exit()

# Example of bidirectional communication

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
            
            # print(user_input1)
            # print(user_input2)
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
