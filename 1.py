# importing libraries
import numpy as np
import cv2 as cv
import time

import HW_interface as HW

filter_window = 10

cropp_f = (
	(65, 380), 	#heigh
	(170, 415)	#width
	)

cam_settings = {
	'blur_kf' : 3, 
	'CNY_kf_bottom' : 125,
	'CNY_kf_up' : 175,
	'threshold' : 2,
	'minLineLength' : 10,
	'maxLineGap' : 5,
	'light' : 100
}

dir_lists = (((list()), (list())), ((list()), (list())))
			

def save_frame(frame, i):
	from datetime import date
	today = date.today()
	time = date.ctime()
	print("Today's date:", today, time)
	filename = today + time + ' ' + str(i) + '.jpg'
	cv.imwrite(filename, frame)

def show_screen_data(frame, string):	
	font_scale = 0.7
	font_RGB = (255, 0, 0)
	font_thinckness = 1
	i = 0
	string = str(string)
	for string in string.split('\n'):
		cv.putText(
			frame,
			string, 
			(10, 20 + i * 13), 
			cv.FONT_HERSHEY_COMPLEX_SMALL, 
			font_scale, 
			font_RGB, 
			font_thinckness)
		i += 1
	return frame


def load_settings(cam_No):

	import json
	import copy

	file_name = "cam_" + str(cam_No) + "_settings.json"

	loaded = {				#КОСТЫЛЬ
		'blur_kf' : 3, 				#КОСТЫЛЬ
		'CNY_kf_bottom' : 125,				#КОСТЫЛЬ
		'CNY_kf_up' : 175,				#КОСТЫЛЬ
		'threshold' : 2,				#КОСТЫЛЬ
		'minLineLength' : 10,				#КОСТЫЛЬ
		'maxLineGap' : 5,				#КОСТЫЛЬ
		'light' : 100				#КОСТЫЛЬ
	}				#КОСТЫЛЬ
	try:				#КОСТЫЛЬ
		file = open(file_name, 'r', encoding='utf8')				#КОСТЫЛЬ
		loaded = json.load(file).copy()				#КОСТЫЛЬ
				#КОСТЫЛЬ
		cam_settings['blur_kf'] = loaded['blur_kf']				#КОСТЫЛЬ
		cam_settings['CNY_kf_up'] = loaded['CNY_kf_up']				#КОСТЫЛЬ
		cam_settings['CNY_kf_bottom'] = loaded['CNY_kf_bottom']				#КОСТЫЛЬ
		cam_settings['threshold'] = loaded['threshold']				#КОСТЫЛЬ
		cam_settings['minLineLength'] = loaded['minLineLength']				#КОСТЫЛЬ
		cam_settings['maxLineGap'] = loaded['maxLineGap']				#КОСТЫЛЬ
		cam_settings['light'] = loaded['light']				#КОСТЫЛЬ


	except FileNotFoundError:
		print("settings are not found, creating defaulf settings file...")
		file = open(file_name, 'w+', encoding='utf8')
		json.dump(cam_settings, file)
	finally:
		file.close()
	print("settings are loaded:")
	print(json.dumps(cam_settings, indent=4, sort_keys=True))
	return cam_settings


def save_settings(cam_No):

	import json

	file_name = "cam_" + str(cam_No) + "_settings.json"

	try:
		file = open(file_name, 'w+', encoding='utf8')
		json.dump(cam_settings, file)
	except FileNotFoundError:
		print("problem")
	finally:
		file.close()
	print("settings are saved:")
	print(json.dumps(cam_settings, indent=4, sort_keys=True))


def image_processing(raw):
	
	blur_kf = cam_settings['blur_kf']
	CNY_kf_up = cam_settings['CNY_kf_up']
	CNY_kf_bottom = cam_settings['CNY_kf_bottom']
	
	raw_gray_sc = cv.cvtColor(raw, cv.COLOR_BGR2GRAY)
	frame_cropped = raw_gray_sc[cropp_f[0][0]: cropp_f[0][1], cropp_f[1][0]: cropp_f[1][1]]
	frame_blured = cv.GaussianBlur(frame_cropped, (blur_kf, blur_kf), cv.BORDER_DEFAULT)
	ret3, frame_devided = cv.threshold(frame_blured,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
	frame_cny = cv.Canny(frame_devided, CNY_kf_bottom, CNY_kf_up)
	
	return frame_devided, frame_cny 

def find_lines(frame_cny):

	threshold = cam_settings['threshold']
	minLineLength = cam_settings['minLineLength']
	maxLineGap = cam_settings['maxLineGap']
	lines = cv.HoughLinesP(frame_cny, 1, np.pi / 180, threshold=threshold, minLineLength=minLineLength, maxLineGap=maxLineGap)
	vek_list = []
	if lines is not None:
		for i in range(0, len(lines)):
			line = lines[i][0]
			point_1 = (line[0] + cropp_f[1][0], line[1] + cropp_f[0][0])
			point_2 = (line[2] + cropp_f[1][0], line[3] + cropp_f[0][0])
			if point_1[1] < point_2[1]:
				point_1, point_2 = point_2, point_1
			vek_list.append((point_1, point_2))
		vek_list = sorted(vek_list, key= lambda x: -x[0][1])
	return vek_list


def draw_lines(frame, vek_list, B = 0, G = 100, R = 255):


	for vek in vek_list:
		cv.line(frame, vek[0], vek[1], (B, G, R), 3, cv.LINE_AA)
		frame = cv.circle(frame, vek[0], 4, (255, 0, 0), 2)
		frame = cv.circle(frame, vek[1], 4, (0, 0, 255), 2)			
	return frame

def calc_direction(vek_list):
	
	if vek_list != False and len(vek_list) > 2:
		direction = ((
			int((vek_list[0][0][0] + vek_list[1][0][0]) / 2),
			int((vek_list[0][0][1] + vek_list[1][0][1]) / 2)),
			(
			int((vek_list[0][1][0] + vek_list[1][1][0]) / 2),
			int((vek_list[0][1][1] + vek_list[1][1][1]) / 2))
					)		
		return direction
	else:
		return ((0,0),(0,0))


def filter(filter_arr, val):
	filter_arr.append(val)
	if len(filter_arr) > filter_window:
		filter_arr.pop(0)
	if len(filter_arr) > 1:
		return int(sum(filter_arr) / len(filter_arr))
	else:
		return filter_arr[0]


def set_camera(cam_No):
	cam = cv.VideoCapture(cam_No)
	
	if (cam.isOpened()== False):
		print("Error opening video file")
		return False
	
	load_settings(cam_No)

	threshold = cam_settings['threshold']
	minLineLength = cam_settings['minLineLength']
	maxLineGap = cam_settings['maxLineGap']
	blur_kf = cam_settings['blur_kf']
	CNY_kf_up = cam_settings['CNY_kf_up']
	CNY_kf_bottom = cam_settings['CNY_kf_bottom']
	light = cam_settings['light']

	HW.set_light(light)

	while(cam.isOpened()):
	
		ret, raw = cam.read()
		if ret == True:

			scrn_data = ('koeffs: \n' +
	
							'blur_kf = ' + str(blur_kf) + ' | W/w\n' +
							'CNY_kf_up =' + str(CNY_kf_up) + ' | R/r\n' +
							'CNY_kf_bottom =' + str(CNY_kf_bottom) + ' | E/e\n' + 
							'\n' + 	
							'Line detection settings: \n' +
							'\n' +
							'threshold = ' + str(threshold) + ' | T/t\n' +
							'minLineLength =' + str(minLineLength) + ' | F/f\n' +
							'maxLineGap =' + str(maxLineGap) + ' | G/g\n' +
							'\n'+
							'light = ' + str(light) + ' | L/l\n' + 
							'save settings: \'s\'' + 
							'exit: \'q\''
							)
			frame_devided, frame_cny = image_processing(raw)

			raw = show_screen_data(raw, scrn_data)
			lines = find_lines(frame_cny)
			draw_lines(raw, lines)
			dir = calc_direction(lines)
			
			filtered_dir = (
				(
					filter(dir_lists[0][0], dir[0][0]),
					filter(dir_lists[0][1], dir[0][1]),
				), 
				(
					filter(dir_lists[1][0], dir[1][0]),
					filter(dir_lists[1][1], dir[1][1]),
				))

			draw_lines(raw, [dir], 255, 0, 255)
			draw_lines(raw, [filtered_dir], 255, 255, 255)

			raw = show_screen_data(raw, scrn_data)

			cv.imshow('raw', raw)
			cv.imshow('devided', frame_devided)
			cv.imshow('cny', frame_cny)


			key = cv.waitKey(25) & 0xFF
	# Press Q on keyboard to exit
			key = cv.waitKey(25) & 0xFF
			if key == ord('q'):
				break

			if key == ord('W'):
				blur_kf += 2
			if key == ord('w'):
				blur_kf -= 2

			if key == ord('E'):
				CNY_kf_bottom += 2
			if key == ord('e'):
				CNY_kf_bottom -= 2

			if key == ord('R'):
				CNY_kf_up += 2
			if key == ord('r'):
				CNY_kf_up -= 2

			if key == ord('T'):
				threshold += 2
			if key == ord('t'):
				threshold -= 2

			if key == ord('F'):
				minLineLength += 2
			if key == ord('f'):
				minLineLength -= 2

			if key == ord('G'):
				maxLineGap += 2
			if key == ord('g'):
				maxLineGap -= 2

			if key == ord('L'):
				light += 2
				HW.set_light(light)
			if key == ord('l'):
				light -= 2
				HW.set_light(light)

			# if key == ord('a'):
				# save_frame(output, i)
				# i += 1
			if key == ord('A'):
				save_frame(raw, i)
				i += 1

			if key == ord('s'):
				cam_settings['blur_kf'] = blur_kf
				cam_settings['CNY_kf_up'] = CNY_kf_up
				cam_settings['CNY_kf_bottom'] = CNY_kf_bottom
				cam_settings['threshold'] = threshold
				cam_settings['minLineLength'] = minLineLength
				cam_settings['maxLineGap'] = maxLineGap
				cam_settings['light'] = light
				save_settings(cam_No)
			time.sleep(0.1)
	cam.release()
	cv.destroyAllWindows()





 
# def find_lines(frame_cny):
# 	cropp_f = (
# 		(65, 380), 	#heigh
# 		(170, 415)	#width
# 		)
# 	# cam = cv.VideoCapture(0)
	
# 	# if (cam.isOpened()== False):
# 		# print("Error opening video file")
# 		# return False
	
# 	# cam_set = load_settings(cam_No)

# 	# blur_kf = cam_set['blur_kf']
# 	# CNY_kf_up = cam_set['CNY_kf_up']
# 	# CNY_kf_bottom = cam_set['CNY_kf_bottom']
# 	threshold = cam_settings['threshold']
# 	minLineLength = cam_settings['minLineLength']
# 	maxLineGap = cam_settings['maxLineGap']
# 	# light = cam_set['light']

# 	# HW.set_light(light)

# 	# while(cam.isOpened()):
	
# 		# ret, raw = cam.read()
# 		# if ret == True:

# 			# scrn_data = ('koeffs: \n' +
	
# 			# 				'blur_kf = ' + str(blur_kf) + ' | W/w\n' +
# 			# 				'CNY_kf_up =' + str(CNY_kf_up) + ' | R/r\n' +
# 			# 				'CNY_kf_bottom =' + str(CNY_kf_bottom) + ' | E/e\n' + 
# 			# 				'\n' + 	
# 			# 				'Line detection settings: \n' +
# 			# 				'\n' +
# 			# 				'threshold = ' + str(threshold) + ' | T/t\n' +
# 			# 				'minLineLength =' + str(minLineLength) + ' | F/f\n' +
# 			# 				'maxLineGap =' + str(maxLineGap) + ' | G/g\n' +
# 			# 				'\n'+
# 			# 				'light = ' + str(light) + ' | L/l\n' + 
# 			# 				'save settings: \'s\'' + 
# 			# 				'exit: \'q\''
# 			# 				)

# 			# raw_gray_sc = cv.cvtColor(raw, cv.COLOR_BGR2GRAY)
# 			# frame_cropped = raw_gray_sc[cropp_f[0][0]: cropp_f[0][1], cropp_f[1][0]: cropp_f[1][1]]
# 			# frame_blured = cv.GaussianBlur(frame_cropped, (blur_kf, blur_kf), cv.BORDER_DEFAULT)
# 			# ret3, frame_devided = cv.threshold(frame_blured,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
# 			# frame_cny = cv.Canny(frame_devided, CNY_kf_bottom, CNY_kf_up)

# 	lines = cv.HoughLinesP(frame_cny, 1, np.pi / 180, threshold=threshold, minLineLength=minLineLength, maxLineGap=maxLineGap)
	
# 	return lines

# 			# raw = show_screen_data(raw, scrn_data)

# 			# cv.imshow('raw', raw)

# 			# key = cv.waitKey(25) & 0xFF
# 			# if key == ord('q'):
# 			# 	break



set_camera(0)
# # find_lines(0)


