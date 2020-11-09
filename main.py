import cv2 as cv
import numpy as np
import os
import keyboard
from time import time, sleep
from capture import WindowCapture
from detection import Detection
from vision import Vision
from functions import BotActions, BotState


DEBUG = True

wincap = WindowCapture('OSBuddy - 6ftclaud')
detector = Detection('machinelearning/cascade.xml')
vision = Vision()
bot = BotActions((wincap.offset_x, wincap.offset_y), (wincap.w, wincap.h))

wincap.start()
detector.start()
bot.start()

while(True):

	if wincap.screenshot is None:
		continue

	detector.update(wincap.screenshot)

	if bot.state == BotState.INITIALIZING:
		targets = vision.get_click_points(detector.rectangles)
		bot.update_targets(targets)
	elif bot.state == BotState.SEARCHING:
		targets = vision.get_click_points(detector.rectangles)
		bot.update_targets(targets)
		bot.update_screenshot(wincap.screenshot)
	elif bot.state == BotState.MOVING:
		bot.update_screenshot(wincap.screenshot)
	elif bot.state == BotState.MINING:
		pass
	elif bot.state == BotState.STASHING:
		#bot.navigate_to(bot.CURRENT_POSITION, bot.BANK)
		#bot.navigate_to(bot.CURRENT_POSITION, bot.MINE)
		wincap.stop()
		detector.stop()
		bot.stop()
		if DEBUG == True:
			cv.destroyAllWindows()
		else:
			pass
		break


	if DEBUG == True:
		detection_image = vision.draw_rectangles(wincap.screenshot, detector.rectangles)
		cv.imshow('Matches', detection_image)
		key = cv.waitKey(1)
		if key == ord('q'):
			wincap.stop()
			detector.stop()
			bot.stop()
			cv.destroyAllWindows()
			break
	elif DEBUG == False:
		if keyboard.is_pressed('q'):
			wincap.stop()
			detector.stop()
			bot.stop()
			break

print('Done.')