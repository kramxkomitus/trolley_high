import serial

string = ''
max_speed = 700

drives_path = "/dev/ttyUSB0"
devices_path = "/dev/ttyUSB1"

while "devices" not in string:
    devices_path, drives_path = drives_path, devices_path  
    devices = serial.Serial(devices_path, baudrate=115200, timeout=0.1)
    drives = serial.Serial(drives_path, baudrate=115200, timeout=0.1)
    devices.write(('whoareyou\n').encode())
    print('whoareyou')
    string = devices.readline().decode('utf-8')
    print(string+'!!!')

drives = serial.Serial(drives_path, baudrate=115200, timeout=0.01)
devices = serial.Serial(devices_path, baudrate=115200, timeout=0.01)

def set_light(B, G, R):
    if devices.isOpen() == False:
        print("error open ", devices_path)
    devices.write((f"l {R} {G} {B}\n").encode())

def init_drives():
    print("finding drives HW:")
    uart = serial.Serial(drives_path, baudrate=115200)
    if uart.isOpen() == True:
        print("found" + drives_path)
    else:
        print("can't reach drives HW" + drives_path)
    uart.write(('stop\n').encode())

def send_drives(str):
    drives.write((str + '\n').encode())

def ask_drives():
    uart = serial.Serial(drives_path, baudrate=115200, timeout=0.01)
    try:
        string = uart.readline().decode('utf-8')
        string != ''
        return string
    except:
        return False


class uart:
    def __init__(self, name):
        for i in range(10):
            try:
                self.path = "/dev/ttyUSB" + str(i)
                self.serial = serial.Serial(self.path, baudrate=115200)
                self.serial.write(('whoareyou\n').encode())
                print("send whoareyou to ", self.path)
                if name in str(self.serial.readline()):
                    self.name = name
                    return
            except:
                continue
