# importing libraries
import numpy as np
import cv2 as cv

import math
import os

def show_screen_data(frame, string):	
	# Вопрос по ООП. Если я хочу сделать это методом како-то внешнего (написанного не мной класса), 
	# то я должен делать какой-то оберточный класс или все же это должно остаться просто функцией.
	font_scale = 0.7
	font_RGB = (200, 0, 0)
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
	
	file_name = "cam_" + str(cam_No) + "_llsettings.json"
	cam_settings = {
		'blur_kf' : 3, 
		'CNY_kf_bottom' : 125,
		'CNY_kf_up' : 175,
		'threshold' : 2,
		'minLineLength' : 10,
		'maxLineGap' : 5}
	try:
		file = open(file_name, 'r', encoding='utf8')
		data = json.load(file)
	except FileNotFoundError:
		print("settings are not found, creating defaulf settings file...")
		file = open(file_name, 'w+', encoding='utf8')
		json.dump(cam_settings, file)
	finally:
		file.close()
	print("settings are loaded:")
	print(json.dumps(cam_settings, indent=4, sort_keys=True))
	return cam_settings

def set_camera(cam_No=0):

	i = 0

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

	while(cam.isOpened()):

		scrn_data_CNY = ('koeffs: \n' +
						'blur_kf = ' + str(blur_kf) + ' | o/p\n' +
						'CNY_kf_up =' + str(CNY_kf_up) + ' | l/,\n' +
						'CNY_kf_bottom =' + str(CNY_kf_bottom) + ' | k/m'
						)
		scrn_data =  ('Line detection settings: \n' +
						'threshold = ' + str(threshold) + ' | w/s\n' +
						'minLineLength =' + str(minLineLength) + ' | e/d\n' +
						'maxLineGap =' + str(maxLineGap) + 'r/f\n' +
						'exit: \'q\''
						)

		ret, frame = cam.read()
		if ret == True:
			raw = frame
			frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
			frame_CNY = cv.GaussianBlur(frame, (blur_kf, blur_kf), cv.BORDER_DEFAULT)
			frame_CNY = cv.Canny(frame_CNY, CNY_kf_bottom, CNY_kf_up)

			lines = cv.HoughLinesP(frame_CNY, 1, np.pi / 180, threshold=threshold, minLineLength=minLineLength, maxLineGap=maxLineGap)
			if lines is not None:
				for i in range(0, len(lines)):
					l = lines[i][0]
					cv.line(frame, (l[0], l[1]), (l[2], l[3]), (0,0,255), 3, cv.LINE_AA)
			
			frame = show_screen_data(frame, scrn_data)
			frame_CNY = show_screen_data(frame_CNY, scrn_data_CNY)
			cv.imshow('camera', raw)
			cv.imshow('original', frame)
			cv.imshow('output', frame_CNY)


		# Press Q on keyboard to exit
			key = cv.waitKey(25) & 0xFF
			if key == ord('q'):
				break

			if key == ord('o'):
				blur_kf += 2
			if key == ord('p'):
				blur_kf -= 2

			if key == ord('k'):
				CNY_kf_bottom += 2
			if key == ord('m'):
				CNY_kf_bottom -= 2

			if key == ord('l'):
				CNY_kf_up += 2
			if key == ord(','):
				CNY_kf_up -= 2

			if key == ord('w'):
				threshold += 2
			if key == ord('s'):
				threshold -= 2

			if key == ord('e'):
				minLineLength += 2
			if key == ord('d'):
				minLineLength -= 2

			if key == ord('r'):
				maxLineGap += 2
			if key == ord('f'):
				maxLineGap -= 2

			if key == ord('z'):
				# raw = show_screen_data(raw, scrn_data)
				save_frame(raw, i)
				i =+ 1
		else:
			break

	cam.release()
	cv.destroyAllWindows()




def save_frame(frame, i):
	import os
  
	# Image directory
	# directory = ./
	filename = '9.12.22' + str(i) + '.jpg'
	cv.imwrite(filename, frame)
  


d = load_settings(0)
type(d)
print(d['blur_kf'])

set_camera(0)






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