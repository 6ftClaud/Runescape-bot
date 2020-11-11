# This .py file is used to generate location-destination-location files for the bot to take after filling up inventory

import win32api
import time
import pyautogui
import keyboard
from capture import WindowCapture

wincap = WindowCapture('OSBuddy - 6ftclaud')

def get_screen_position(pos):
    return pos
    #return (pos[0] + wincap.offset_x, pos[1] + wincap.offset_y)

print("Started.")

state_left = win32api.GetKeyState(0x01)
state_right = win32api.GetKeyState(0x02)

file = open('navigation/recording.txt', 'w')
start = time.time()
while True:
    a = win32api.GetKeyState(0x01)
    b = win32api.GetKeyState(0x02)

    if a != state_left:
        state_left = a
        if a < 0:
            x,y = pyautogui.position()
            if a < 0:
                now = time.time()
                loop_time = now - start
                pos = ((x, y))
                pos = get_screen_position((x, y))
                x, y = pos
                pos = None
                pos = str(x) + " " + str(y) + " " + str(loop_time) + "\n"
                print(pos)
                file.write(pos)
                start = time.time()
    if b != state_right:
        state_right = b
        if b < 0:
            x,y = pyautogui.position()
            if b < 0:
                now = time.time()
                loop_time = now - start
                pos = ((x, y))
                pos = get_screen_position((x, y))
                x, y = pos
                pos = None
                pos = str(x) + " " + str(y) + " " + str(loop_time) + "\n"
                print(pos)
                file.write(pos)
                start = time.time()
    elif keyboard.is_pressed('ESC'):
        	break
    time.sleep(0.001)

file.close()