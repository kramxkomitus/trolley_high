import serial
import time
serial_path = "/dev/ttyUSB0"
HW = serial.Serial(serial_path, baudrate=115200)
if HW.isOpen() == True:
    print("found" + serial_path)
HW.write(("w 0 0 255\r").encode())
time.sleep(0.1)

HW.write(("w 255 255 255\r").encode())
