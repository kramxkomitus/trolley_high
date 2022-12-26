import serial
drives_path = "/dev/ttyUSB0"
devices_path = "/dev/ttyUSB1"



drives = serial.Serial(drives_path, baudrate=115200, timeout=0.01)
drives.write(('whoareyou\n').encode())
string = drives.readline().decode('utf-8')
if string != "drives":
    drives_path = "/dev/ttyUSB0"
    devices_path = "/dev/ttyUSB1"


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
    drives.write((str + '\n').encode())

def ask_drives():
    uart = serial.Serial(drives_path, baudrate=115200, timeout=0.01)
    string = uart.readline().decode('utf-8')
    if string != '':
        return string
    else:
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
