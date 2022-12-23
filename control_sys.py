import HW_interface as HW
import simple_pid
from simple_pid import PID
import time
import machine_vision as MV
import cv2 as cv

L_vel, R_vel = int(), int()
max_speed = 1000


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
    # P, I, D = load_pid_settings('1')
    # pid = PID(P, I, D)
    # pid.setpoint = 0
    # pid.sample_time(1)

    cam_No = 0
    cam_settings = MV.load_settings(cam_No)

    # threshold = cam_settings['threshold']
    # minLineLength = cam_settings['minLineLength']
    # maxLineGap = cam_settings['maxLineGap']
    # blur_kf = cam_settings['blur_kf']
    # CNY_kf_up = cam_settings['CNY_kf_up']
    # CNY_kf_bottom = cam_settings['CNY_kf_bottom']
    light = cam_settings['light']
    
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
            angle, dir = MV.calc_mean_dir(mean_line)
            N = ((320, 480), (320 + dir[0], 240 + dir[1]))
            MV.draw_lines(raw, [N, mean_line], 255, 0, 255)

            time_period, cur_time = time.monotonic() - cur_time, time.monotonic()

            scrn_data = 'angle: ' + str(angle) + '\ntime: ' + f'{time_period:.3f}' + 'sec'
            raw = MV.show_screen_data(raw, scrn_data)
            cv.imshow('control', raw)
            
            key = cv.waitKey(25) & 0xFF
            if key == ord('q'):
                break
        
            # pid.update(angle)
            # delta = pid.output()
            delta =4
            left = max_speed
            right= max_speed
            if angle > 0:
                left -= delta
            else:
                right -= delta
            print(str(left) + "       " + str(right) + '\t\t\t\t', end='')
    
            R_str = "R " + str(right)
            L_str = "L " + str(left)

        # HW.write(('R' + str(right) + '\n').encode())
        # HW.write((L_str + '\n').encode())
        # time.sleep(0.001)


    cam.release()
    cv.destroyAllWindows()

control()