import evdev
from evdev import ecodes
import subprocess 
import HW_interface as HW
import control_sys as CS

controller_MAC = "C8:3F:26:B8:00:16"

def find_gamepad():
    
    print("finding gamepad, MAC:" + controller_MAC)
    output = ""
    while ("Connection successful" or "Connected: yes") not in output:
        output = subprocess.getoutput("bluetoothctl connect " + controller_MAC)
        print(output)
    
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        if "Xbox Wireless Controller" in device.name:
            print("find controller", device.path, device.name, device.phys)
            return device
        else:
            print("error")
            return False

HW.send_drives('stop')
left_dir = 1
right_dir = 1
left_abs = 0
right_abs = 0

Joystik = find_gamepad()
feedback = ''


if Joystik != False: 
    # for event in Joystik.read_loop():
    for event in Joystik.read_loop():
        if event !=  None:
            if event.type == ecodes.EV_KEY:
                # A button
                if event.code == 304 and not event.value:
                    print("\n\t\t start \n")
                    HW.send_drives("start")
                # B button
                if event.code == 305 and not event.value:
                    print("\n\t\t stop \n")
                    HW.send_drives("stop")
                # Left bump
                if event.code == 310:
                    if event.value:
                        left_dir = -1
                    else:
                        left_dir = 1
                # Right bump[]
                if event.code == 311:
                    if event.value:
                        right_dir = -1
                    else:
                        right_dir = 1   

                # start autonomous
                if event.code == 158:
                    if not event.value:
                        CS.control(Joystik)

            elif event.type == ecodes.EV_ABS:
                # left trigger
                if event.code == 10:
                    left_abs = event.value
                # right trigger
                elif event.code == 9:
                    right_abs = event.value

                left = left_abs * left_dir
                right = right_abs * right_dir
                responde = HW.ask_drives()
                if responde != False:
                    feedback = responde
                HW.send_drives("L " + str(left))
                HW.send_drives("R " + str(right))
                print("L ", left, "\t\t\tR ", right, "\t\t\t\t\tFeedback: ", feedback[:-1])
