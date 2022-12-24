import HW_interface as HW
from simple_pid import PID
import time
import machine_vision as MV
import cv2 as cv
import HW_interface as HW

L_vel, R_vel = int(), int()
max_speed = 600


def load_pid_settings(name):

	import json
	file_name = "PID_settings_" + str(name)+ ".json"
	loaded = {
        'P' : -1,
        'I' : -1,
        'D' : -1
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


def save_settings(name, P, I, D):

	import json
	file_name = "PID_settings_" + str(name)+ ".json"
	loaded = {
        'P' : P,
        'I' : I,
        'D' : D
        }
	try:
		file = open(file_name, 'w+', encoding='utf8')
		json.dump(loaded, file)
	except FileNotFoundError:
		print("error")  
	finally:
		file.close()



        #разделить нормально функции, произвести детект, произвести расчет. выдать это в пид
def control():
    P, I, D = load_pid_settings('1')
    pid = PID(P, I, D)
    pid.setpoint = 0
    pid.sample_time = 0.5
    pid.output_limits = (-max_speed, max_speed)
    delta_arr = []
    time_period = 0
    delta = 0

    cam_No = 0
    cam_settings = MV.load_settings(cam_No)
    watch_dog = 0

    # threshold = cam_settings['threshold']
    # minLineLength = cam_settings['minLineLength']
    # maxLineGap = cam_settings['maxLineGap']
    # blur_kf = cam_settings['blur_kf']
    # CNY_kf_up = cam_settings['CNY_kf_up']
    # CNY_kf_bottom = cam_settings['CNY_kf_bottom']
    light = cam_settings['light']
    HW.send_drives('start')
    
    HW.set_light(light)

    cam = cv.VideoCapture(cam_No)

    if (cam.isOpened()== False):
        print("Error opening video file")
        return False
    
    cur_time = time.monotonic()
	
    while(cam.isOpened()):
        ret, raw = cam.read()
        if ret == True:
            frame_devided, frame_cny = MV.image_processing(raw)
            lines = MV.find_lines(frame_cny)
            mean_line = MV.find_mean_direction(lines)
            if mean_line == ((0, 0),(0, 0)):
                time.sleep(0.1)
                angle, dir = 0, (0, 1)
                watch_dog += 1
                # continue
            if watch_dog == 1000000:
                break
            watch_dog = 0
            angle, dir = MV.calc_mean_dir(mean_line)


            delta = pid(angle)
            left = max_speed
            right= max_speed
            if delta < 0:
                right = right + int(delta)
            else:
                left = left - int(delta)

            R_str = "R " + str(right+10)
            L_str = "L " + str(left+10)
            print(L_str + '\t\t\t' + R_str)

            scrn_data = 'angle: ' + str(angle) + '\ntime: ' + f'{time_period:.3f}' + 'sec' \
            + str(mean_line) + '\n P, I, D: ' + str((P, I, D))
            scrn_data += '\n delta = ' + str(delta)
            scrn_data += '\n left = ' + str(left) + ' right = ' + str(right)

            N = ((320, 480), (320 + dir[0], 480 + dir[1]))
            L = ((10, 240), (10, int(left / 4)))
            R = ((630, 240), (630, int(right / 4)))
            MV.draw_lines(raw, lines, 255, 0, 255)
            MV.draw_lines(raw, [L, R], 0, 200, 100)
            MV.draw_lines(raw, [N], 0, 0, 255)

            HW.send_drives(L_str)
            time.sleep(0.001)
            HW.send_drives(R_str)

            time_period, cur_time = time.monotonic() - cur_time, time.monotonic()
            sleeping = pid.sample_time - time_period
            if sleeping < 0:
                print('\n ERROR')
                sleeping = 0
                # continue
            time.sleep(sleeping)
            raw = MV.show_screen_data(raw, scrn_data)
            # cv.imshow('control', raw)
            cv.imshow('detector', frame_devided)

            key = cv.waitKey(25) & 0xFF
            if key == ord('q'):
                break
            if key == ord('P'):
                P += 1
            if key == ord('p'):
                P -= 1
            if key == ord('I'):
                I += 0.1
            if key == ord('i'):
                I -= 0.1
            if key == ord('D'):
                D += 1
            if key == ord('d'):
                D -= 1
            if key == ord('s'):
                save_settings(P, I, D)
            if key == ord('w'):    
                pid = PID(P, I, D)
                pid.setpoint = 0
                pid.sample_time = 0.5
                pid.output_limits = (-max_speed, max_speed)

    cam.release()
    cv.destroyAllWindows()
    R_str = "R " + str(10)
    L_str = "L " + str(10)
    HW.send_drives(R_str)
    HW.send_drives(L_str)
    print(L_str + '\t\t\t' + R_str)
    
    

control()