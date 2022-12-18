import evdev
from evdev import ecodes
import time 
import subprocess 
import os
import HW_interface as HW

controller_MAC = "C8:3F:26:B8:00:16"

L_vel = 0
R_vel = 0

left = 0
right = 0

moment = 0

def set_vel(R, L):
    if moment < time.time_ns + 1000:
        return

    moment = time.time_ns
    global L_vel, R_vel
    if R == 0:
        R_vel = 0
    elif R > R_vel >= 0 :
        R_vel += 1
    elif R_vel > R:
        R_vel -= 1

    if L == 0:
        L_vel = 0
    elif L > L_vel >= 0 :
        L_vel += 1
    elif L_vel > L:
        L_vel -= 1


def find_gamepad():
    
    print("finding gamepad, MAC:" + controller_MAC)
    output = ""
    while "Connection successful" not in output:
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

HW.init_drives()
HW.send_drives('stop')
left_dir = 1
right_dir = 1
left_abs = 0
right_abs = 0

Joystik = find_gamepad()


if Joystik != False: 
    # for event in Joystik.read_loop():
    moment = 0
    while True:
        event = Joystik.read_one()    # buttons
        if event !=  None:

            if event.type == ecodes.EV_KEY:
                # A button
                if event.code == 304 and not event.value:
                    print("\n\n\n start \n\n\n")
                    HW.send_drives("start")
                # B button
                if event.code == 305 and not event.value:
                    print("\n\n\n stop \n\n\n")
                    HW.send_drives("stop")
                # Left bump
                if event.code == 310:
                    if event.value:
                        left_dir = -1
                    else:
                        left_dir = 1
                # Right bump
                if event.code == 311:
                    if event.value:
                        right_dir = -1
                    else:
                        right_dir = 1   

            elif event.type == ecodes.EV_ABS:
                if event.code == 10:
                    left_abs = event.value

                    # elif event.code == 9:
                        # right_abs = event.value

                    left = left_abs * left_dir
                    # right = right_abs * right_dir
                    set_vel(left, 0)   
                    print(L_vel, "\t\t\t", 0)

    # HW.send_drives("R " + str(R_vel))
    # HW.send_drives("R " + str(R_vel))
    # time.sleep(0.005)

