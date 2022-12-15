import serial
import time
serial_path = "/dev/ttyUSB0"
HW = serial.Serial(serial_path, baudrate=115200)
if HW.isOpen() == True:
    print("found" + serial_path)
HW.write(("w 0 255 255\n").encode())

