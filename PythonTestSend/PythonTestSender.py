import serial
import time
import struct  # For packing floats into bytes

# Configure the serial connection
ser = serial.Serial('COM6', 115200)
time.sleep(2) # Wait for the connection to establish

try:
    while True:
        float_to_send = float(input("Enter a float to send to Arduino: "))
        bytecode = struct.pack('f', float_to_send)
        ser.write(bytecode)  # Send data as bytes
        print(f"Sent: {float_to_send}")
except KeyboardInterrupt:
    print("Exiting program.")
finally:
    ser.close()
