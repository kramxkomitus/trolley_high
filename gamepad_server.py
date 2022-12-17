import pygame
import serial
import time 
import subprocess 
import os


L_vel = 0
R_vel = 0

def trig_func(axis):
    
    axis = int(500 * (axis + 1))
    if axis < 1:
        return 0
    else:
        return axis

def set_vel(R, L):
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
    return




controller_MAC = "C8:3F:26:B8:00:16"

print("finding gamepad, MAC:" + controller_MAC)
# output = subprocess.getoutput("bluetoothctl scan on")
output = ""
while "Connection successful" not in output:
    output = subprocess.getoutput("bluetoothctl connect " + controller_MAC)
    print(output)

print("finding TTL:")
serial_path = "/dev/ttyUSB0"
HW = serial.Serial(serial_path, baudrate=115200)
if HW.isOpen() == True:
    print("found" + serial_path)
else:
    print("can't reach " + serial_path)
pygame.init()

print("initial video")

# os.environ["SDL_VIDEODRIVER"] = "dummy"
print("success")


pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

left = 0
right = 0

while True:
    pygame.event.pump()
    A = joystick.get_button(0)
    B = joystick.get_button(1)
    X = joystick.get_button(2)
    Y = joystick.get_button(0)

    left_inv, right_inv = joystick.get_button(6), joystick.get_button(7)
    left, right = joystick.get_axis(4), joystick.get_axis(5)


    if A:
        HW.write(f"start\n".encode())
        A = 0
        print("start")
    if B:
        HW.write(f"stop\n".encode())
        B = 0
        print("stop")

    left = trig_func(left)
    right = trig_func(right)

    set_vel(left, right)



    R_str = "R " + str(R_vel * (1 - 2 * right_inv))
    L_str = "L " + str(L_vel * (1 - 2 * left_inv))
    print(L_str + "       " + R_str + '\r')
    HW.write((R_str + '\n').encode())
    HW.write((L_str + '\n').encode())
    time.sleep(0.001)
    
    




# while True:
#     serial_path = "/dev/ttyUSB1"
#     #  + str(i)
#     HW = serial.Serial(serial_path, baudrate=115200)
#     if HW.isOpen() == True:
#         print("found" + serial_path)
#         break
#     print("can't reach " + serial_path)
    

# pygame.init()
