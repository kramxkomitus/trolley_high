import HW_interface as HW

L_vel, R_vel = int(), int()
max_speed = 1000

def set_vel(L, R):
    global L_vel, R_vel

    if R == 0:
        if R_vel > 0:
            R_vel -= 1
        elif R_vel < 0:
            R_vel += 1

    elif (-max_speed  < R_vel) and (R_vel > R): 
        R_vel -= 1

    elif (max_speed > R_vel) and ( R_vel < R):
        R_vel += 1
    

    if L == 0:
        if L_vel > 0:
            L_vel -= 1
        elif L_vel < 0:
            L_vel += 1

    elif (-max_speed  < L_vel) and (L_vel > L): 
        L_vel -= 1

    elif (max_speed > L_vel) and ( L_vel < L):
        L_vel += 1

    return



def load_pid_settings(name):

	import json
	file_name = "PID_settings_" + str(name)+ ".json"
	loaded = {
        'P' : 1,
        'I' : 1,
        'D' : 1
        }
	try:
		file = open(file_name, 'r', encoding='utf8')
		loaded = json.load(file).copy()
		P = loaded['P']
		I = loaded['I']
		D = loaded['D']		
	except FileNotFoundError:
		print("settings are not found, creating defaulf settings file...")
		file = open(file_name, 'w+', encoding='utf8')
		json.dump(loaded, file)
	finally:
		file.close()
	print("settings are loaded:")
	print(json.dumps(loaded, indent=4, sort_keys=True))
	return P, I, D


# def save_settings(name, P, I, D):
# 	import json
# 	file_name = ("PID__settings" + str(name) + ".json") 
# # try:
#     file = open(file_name, 'w+', encoding='utf8')
#     #     loaded = dict()
    #     loaded['P'] = P
    # 	loaded['I'] = I
    # 	loaded['D']	= D
    # 	json.dump(cam_settings, file)
    # except FileNotFoundError:
    # 	print("problem")
    # finally:
    # 	file.close()
    # print("settings are saved:")
    # print(json.dumps(cam_settings, indent=4, sort_keys=True))


import simple_pid
from simple_pid import PID
import time
import machine_vision as MV
left = max_speed
right = max_speed

P, I, D = load_pid_settings('1')


pid = PID(P, I, D)
pid.setpoint = 0
pid.sample_time(0.5)

while(True):
    #разделить нормально функции, произвести детект, произвести расчет. выдать это в пид

    angle = MV.get_direction()
    pid.update(angle)
    delta = pid.output
    #отправить эту дельту на движки


print(str(left) + "       " + str(right) + '\t\t\t\t', end='')
set_vel(left, right)

R_str = "R " + str(R_vel)
L_str = "L " + str(L_vel)

print(L_str + "       " + R_str + '\r')
HW.write((R_str + '\n').encode())
HW.write((L_str + '\n').encode())
time.sleep(0.001)