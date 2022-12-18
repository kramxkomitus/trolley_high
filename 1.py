# importing libraries
import numpy as np
import cv2 as cv
import HW_interface as HW

import math
import os


def show_screen_data(frame, string):	
	# Вопрос по ООП. Если я хочу сделать это методом како-то внешнего (написанного не мной класса), 
	# то я должен делать какой-то оберточный класс или все же это должно остаться просто функцией.
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
	
	file_name = "cam_" + str(cam_No) + "_settings.json"
	cam_settings = {
		'blur_kf' : 3, 
		'CNY_kf_bottom' : 125,
		'CNY_kf_up' : 175,
		'threshold' : 2,
		'minLineLength' : 10,
		'maxLineGap' : 5,
		'light' : 100
		}
	try:
		file = open(file_name, 'r', encoding='utf8')
		cam_settings = json.load(file)
	except FileNotFoundError:
		print("settings are not found, creating defaulf settings file...")
		file = open(file_name, 'w+', encoding='utf8')
		json.dump(cam_settings, file)
	finally:
		file.close()
	print("settings are loaded:")
	print(json.dumps(cam_settings, indent=4, sort_keys=True))
	return cam_settings


def save_settings(cam_No, cam_settings):

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


  
def set_camera(cam_No):
	cropp_f = (
		(65, 380), 	#heigh
		(170, 415)	#width
		)
	cam = cv.VideoCapture(cam_No)
	
	if (cam.isOpened()== False):
		print("Error opening video file")
		return False
	
	cam_set = load_settings(cam_No)

	blur_kf = cam_set['blur_kf']
	CNY_kf_up = cam_set['CNY_kf_up']
	CNY_kf_bottom = cam_set['CNY_kf_bottom']
	threshold = cam_set['threshold']
	minLineLength = cam_set['minLineLength']
	maxLineGap = cam_set['maxLineGap']
	light = cam_set['light']

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

			raw_gray_sc = cv.cvtColor(raw, cv.COLOR_BGR2GRAY)

			frame_cropped = raw_gray_sc[cropp_f[0][0]: cropp_f[0][1], cropp_f[1][0]: cropp_f[1][1]]
			
			frame_blured = cv.GaussianBlur(frame_cropped, (blur_kf, blur_kf), cv.BORDER_DEFAULT)
			
			ret3, frame_devided = cv.threshold(frame_blured,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
			
			frame_cny = cv.Canny(frame_devided, CNY_kf_bottom, CNY_kf_up)



			lines = cv.HoughLinesP(frame_cny, 1, np.pi / 180, threshold=threshold, minLineLength=minLineLength, maxLineGap=maxLineGap)

# 			добавим список линий
			vek = []

			if lines is not None:
				for i in range(0, len(lines)):

					line = lines[i][0]

					point_1 = (line[0] + cropp_f[1][0], line[1] + cropp_f[0][0])

					point_2 = (line[2] + cropp_f[1][0], line[3] + cropp_f[0][0])

					vek.append((point_1, point_2))

					# cv.line(raw, (0, point_1[1]), (600, point_1[1]), (0,100,0), 3, cv.LINE_AA)

					cv.line(raw, point_1, point_2, (0,100,255), 3, cv.LINE_AA)
					raw = cv.circle(raw, point_1, 4, (255, 0, 0), 2)
					raw = cv.circle(raw, point_2, 4, (0, 0, 255), 2)
			# сортировка линий по самым близким

			vek_sort = sorted(vek, key= lambda x: -x[0][1])

			if len(vek_sort) > 1:
				raw = cv.circle(raw, vek_sort[0][0], 10, (0, 255, 0), 2)
				raw = cv.circle(raw, vek_sort[1][0], 10, (0, 255, 0), 2)

				direction = ((
					int((vek_sort[0][0][0] + vek_sort[1][0][0]) / 2),
					int((vek_sort[0][0][1] + vek_sort[1][0][1]) / 2)),
					(
					int((vek_sort[0][1][0] + vek_sort[1][1][0]) / 2),
					int((vek_sort[0][1][1] + vek_sort[1][1][1]) / 2))
				)
			
				cv.line(raw, direction[0], direction[1], (255,100,255), 3, cv.LINE_AA)
				
				from numpy.linalg import norm

				dir = (direction[0][0] - direction[1][0],  direction[0][1] - direction[1][1])
				cos_angle = np.dot(dir, (1, 0)) / norm(dir)
				tetha = np.arccos(cos_angle)

				scrn_data = scrn_data + "\n " + str(tetha)
			# frame_devided = cv.adaptiveThreshold(frame_blured, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
			# frame_devided = cv.adaptiveThreshold(frame_blured, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 2)



			raw = show_screen_data(raw, scrn_data)

			cv.imshow('raw', raw)
			cv.imshow('devided', frame_devided)
			cv.imshow('cny', frame_cny)
			# cv.imshow('output', frame_cropped)


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

			if key == ord('s'):
				cam_set['blur_kf'] = blur_kf
				cam_set['CNY_kf_up'] = CNY_kf_up
				cam_set['CNY_kf_bottom'] = CNY_kf_bottom
				cam_set['threshold'] = threshold
				cam_set['minLineLength'] = minLineLength
				cam_set['maxLineGap'] = maxLineGap
				cam_set['light'] = light
				save_settings(cam_No, cam_set)
	cam.release()
	cv.destroyAllWindows()





 
def find_lines(cam_No):
	cropp_f = (
		(65, 380), 	#heigh
		(170, 415)	#width
		)
	cam = cv.VideoCapture(cam_No)
	
	if (cam.isOpened()== False):
		print("Error opening video file")
		return False
	
	cam_set = load_settings(cam_No)

	blur_kf = cam_set['blur_kf']
	CNY_kf_up = cam_set['CNY_kf_up']
	CNY_kf_bottom = cam_set['CNY_kf_bottom']
	threshold = cam_set['threshold']
	minLineLength = cam_set['minLineLength']
	maxLineGap = cam_set['maxLineGap']
	light = cam_set['light']

	HW.set_lightt(light)

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

			raw_gray_sc = cv.cvtColor(raw, cv.COLOR_BGR2GRAY)
			frame_cropped = raw_gray_sc[cropp_f[0][0]: cropp_f[0][1], cropp_f[1][0]: cropp_f[1][1]]
			frame_blured = cv.GaussianBlur(frame_cropped, (blur_kf, blur_kf), cv.BORDER_DEFAULT)
			ret3, frame_devided = cv.threshold(frame_blured,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
			frame_cny = cv.Canny(frame_devided, CNY_kf_bottom, CNY_kf_up)

			lines = cv.HoughLinesP(frame_cny, 1, np.pi / 180, threshold=threshold, minLineLength=minLineLength, maxLineGap=maxLineGap)

			raw = show_screen_data(raw, scrn_data)

			cv.imshow('raw', raw)

			key = cv.waitKey(25) & 0xFF
			if key == ord('q'):
				break


# def draw_lines(image, cropp_f, lines):
# 	if lines is not None:
# 		for i in range(0, len(lines)):
# 			line = lines[i]

# 			point_1 = (line[0] + cropp_f[1][0], line[1] + cropp_f[0][0])
# 			point_2 = (line[2] + cropp_f[1][0], line[3] + cropp_f[0][0])

# 			cv.line(image, point_1, point_2, (0,100,255), 3, cv.LINE_AA)
# 			raw = cv.circle(image, point_1, 2, (200, 0, 0), 2)
# 			raw = cv.circle(image, point_2, 2, (200, 0, 0), 2)
# 	return raw


set_camera(0)
find_lines(0)

			# frame_CNY = cv.Canny(frame_CNY, CNY_kf_bottom, CNY_kf_up)

			# lines = cv.HoughLinesP(frame_CNY, 1, np.pi / 180, threshold=threshold, minLineLength=minLineLength, maxLineGap=maxLineGap)


			# if lines is not None:
			# 	for i in range(0, len(lines)):
			# 		l = lines[i][0]
			# 		cv.line(frame, (l[0], l[1]), (l[2], l[3]), (0,0,255), 3, cv.LINE_AA)
			


# def save_frame(frame, i):
# 	from datetime import date
# 	# Image directory
# 	# directory = ./


# 	today = date.today()
# 	print("Today's date:", today)

# 	filename = '9.12.22' + str(i) + '.jpg'
# 	cv.imwrite(filename, frame)



			# lines = sorted(lines_raw, reverse=True)


			# # Draw the lines
			# if lines is not None:
			# 	for i in range(0, 5):
			# 		rho = lines[i][0][0]
			# 		theta = lines[i][0][1]
			# 		a = math.cos(theta)
			# 		b = math.sin(theta)
			# 		x0 = a * rho
			# 		y0 = b * rho
			# 		pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
			# 		pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
			# 		cv.line(frame, pt1, pt2, (0,0,255), 3, cv.LINE_AA)





