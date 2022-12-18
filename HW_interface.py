import serial
drives_path = "/dev/ttyUSB1"
devices_path = "/dev/ttyUSB0"

def set_light(val):
    uart = serial.Serial(devices_path, baudrate=115200)
    if uart.isOpen() == False:
        print("error open ", devices_path)
    uart.write(("w " + 3 * (" " + str(val)) + "\n").encode())

def init_drives():
    print("finding drives HW:")
    uart = serial.Serial(drives_path, baudrate=115200)
    if uart.isOpen() == True:
        print("found" + drives_path)
    else:
        print("can't reach drives HW" + drives_path)
    uart.write(('stop\n').encode())

def send_drives(str):
    uart = serial.Serial(drives_path, baudrate=115200)
    uart.write((str + '\n').encode())

