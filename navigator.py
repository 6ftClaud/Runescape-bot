import pyautogui
from time import sleep

class Navigator:

	coordinates = []
	pos = []
	x = 0
	y = 0

	def ToVillage(self):
		with open('tovillage.txt','r') as file:
			for line in file:
				for word in line.split():
					self.pos.append(word)
					self.coordinates.extend(list(self.pos))
					self.pos.clear()

		x_coords = []
		y_coords = []
		time = []
		button = []
		x_coords = self.coordinates[::4]
		y_coords = self.coordinates[1::4]
		time = self.coordinates[2::4]
		button = self.coordinates[3::4]

		for x in range(len(x_coords)):
			print(f"Going to bank: {x_coords[x]}, {y_coords[x]}")
			pyautogui.click(button=str(button[x]), x = int(x_coords[x]), y = int(y_coords[x]))
			sleep(float(time[x]))
		try:
			print("Looking for bank")
			x, y = pyautogui.locateCenterOnScreen('bank.png', confidence = 0.5)
			pyautogui.click(x, y)
			sleep(10)
		except TypeError:
			x, y = pyautogui.locateCenterOnScreen('bank.png', confidence = 0.5)
			pyautogui.click(x, y)
			sleep(10)
		try:
			print("Looking for bank booth")
			x, y = pyautogui.locateCenterOnScreen('bank1.png', confidence = 0.8)
			pyautogui.click(x, y + 25)
			sleep(0.1)
			pyautogui.click(x, y + 50)
			sleep(3)
		except TypeError:
			while pyautogui.locateCenterOnScreen('bank2.png', confidence = 0.7) is None:
				x, y = pyautogui.locateCenterOnScreen('bank1.png', confidence = 0.8)
				pyautogui.click(x, y + 25)
				sleep(0.1)
				pyautogui.click(x, y + 50)
				sleep(3)
		try:
			print("Stashing items")
			x, y = pyautogui.locateCenterOnScreen('bank2.png', confidence = 0.7)
			pyautogui.click(x, y)
		except TypeError:
			x, y = pyautogui.locateCenterOnScreen('bank2.png', confidence = 0.7)
			pyautogui.click(x, y)
		self.ToMine()

	def ToMine(self):
		self.coordinates.clear()
		with open('tomine.txt','r') as file:
			for line in file:
				for word in line.split():
					self.pos.append(word)
					self.coordinates.extend(list(self.pos))
					self.pos.clear()

		x_tomine = []
		y_tomine = []
		time_tomine = []
		button_tomine = []
		x_tomine = self.coordinates[::4]
		y_tomine = self.coordinates[1::4]
		time_tomine = self.coordinates[2::4]
		button_tomine = self.coordinates[3::4]
		for x in range(len(x_tomine)):
			print(f"Going to mine: {x_tomine[x]}, {y_tomine[x]}")
			pyautogui.click(button=str(button_tomine[x]), x = int(x_tomine[x]), y = int(y_tomine[x]))
			sleep(float(time_tomine[x]))
		try:
			print("Arriving at mine")
			x, y = pyautogui.locateCenterOnScreen('mine.png', confidence = 0.7)
			pyautogui.click(x, y - 10)
			sleep(8)
		except TypeError:
			x, y = pyautogui.locateCenterOnScreen('mine.png', confidence = 0.7)
			pyautogui.click(x, y - 10)
			sleep(8)