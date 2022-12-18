import serial
drives_path = "/dev/ttyUSB1"
devices_path = "/dev/ttyUSB0"

def set_light(val):
    HW = serial.Serial(devices_path, baudrate=115200)
    if HW.isOpen() == False:
        print("error open ", devices_path)
    HW.write(("w " + 3 * (" " + str(val)) + "\n").encode())
