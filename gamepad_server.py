import pygame
import serial
import time 
import subprocess 
from math import sqrt


controller_MAC = "C8:3F:26:B8:00:16"

print("finding gamepad, MAC:" + controller_MAC)
output = ""
while "Connection successful" not in output:
    output = subprocess.getoutput("bluetoothctl connect " + controller_MAC)
    print(output)

print("finding TTL:")
i = 0
while True:
    serial_path = "/dev/ttyUSB" + str(i)
    HW = serial.Serial(serial_path, baudrate=115200)
    if HW.isOpen() == True:
        print("found" + serial_path)
        break
    print("can't reach " + serial_path)
    

pygame.init()
pygame.display.init()
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
    left, right = joystick.get_axis(5), joystick.get_axis(4)
    
    # left = (485 * (left + 1) + 1)
    # right = (485  * (right + 1) + 1)
    # left = int(1000 - 1000 / sqrt(left))
    # right = int(1000 - 1000 / sqrt(right))
    
    if left_inv:
        left = -left
    if right_inv:
        right = -right

    if A:
        HW.write(f"start\n".encode())
    if B:
        HW.writable(f"stop\n".encode())

    print(f"{left:.2f}" + "\t\t\t" +f"{right:.2f}")

    # print(f"{left}" + "\t\t\t" + f"{right}")
    # HW.write(f"R {right}\n".encode())
    # time.sleep(0.1)
    # HW.write(f"L {left}\n".encode())
    






# # Main loop
# while True:
#     pygame.event.pump()
#     rt, lt = joystick. get_axis(0), joystick.get_axis(3)
#     rt = max(0, min(rt, 1))
#     lt = max(0, min(lt, 1))

#     start, stop = joystick.get_button(0), joystick.get_button(1)

#     # Send the joystick position to the WebSocket
#     data = f"{rt},{lt}"
#     # ,{start},{stop}"
#     print(data)
#     # s.sendall(data.encode())

#     # Wait a bit before sending the next position
#     time.sleep(0.1)




# # Set up the Wi-Fi connection
# HOST = '127.0.0.1'  # IP address of the PC
# PORT = 8888
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.bind((HOST, PORT))
# s.listen()
# conn, addr = s.accept()
