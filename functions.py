import cv2 as cv
import pyautogui
import random
from PIL import ImageGrab
from time import sleep, time
from threading import Thread, Lock
from math import sqrt


class BotState:
    INITIALIZING = 0
    SEARCHING = 1
    MOVING = 2
    MINING = 3
    STASHING = 4

class BotActions:

    # settings
    INITIALIZING_SECONDS = 2
    MOVEMENT_STOPPED_THRESHOLD = 0.9
    TOOLTIP_MATCH_THRESHOLD = 0.4
    # targets further away from this will be removed
    SEARCH_RADIUS = 400 # pixels
    MAX_MINING_TIME = 6
    STASHING_PATH = 'navigation/stashing.txt' # will follow this path to stash items

    # threading
    stopped = True
    lock = None

    # properties
    state = None
    targets = []
    screenshot = None
    timestamp = None
    movement_screenshot = None
    mining_tooltip = None
    window_offset = (0,0)
    window_w = 0
    window_h = 0
    item_count = 0

    def __init__(self, window_offset, window_size):
        self.lock = Lock()

        self.mining_tooltip = cv.imread('images/mining_tooltip.jpg', cv.IMREAD_UNCHANGED)

        self.window_offset = window_offset
        self.window_w = window_size[0]
        self.window_h = window_size[1]

        self.state = BotState.INITIALIZING
        print("< Starting threads >")
        self.timestamp = time()

        # finds the next target and clicks on it if tooltip is there
    def click_next_target(self):
        targets = self.targets_ordered_by_distance(self.targets)
        target_i = random.randint(0, len(targets))
        found_copper = False

        while not found_copper and target_i < len(targets):
            if self.stopped:
                break

            target_pos = targets[target_i]
            screen_x, screen_y = self.get_screen_position(target_pos)
            pyautogui.moveTo(x=screen_x, y=screen_y)
            sleep(0.1)

            if self.confirm_tooltip(target_pos):
                pyautogui.click(button='right')
                sleep(0.02)
                pyautogui.click(x=screen_x, y=screen_y + 25)
                # prevent tooltip from showing up
                pyautogui.moveTo(1, 1)
                print('Mining at X:{}, Y:{}'.format(screen_x, screen_y))
                found_copper = True
                return found_copper

            target_i += 1

            # targets closer to screen center will be the first targets
    def targets_ordered_by_distance(self, targets):
        my_pos = (self.window_w / 2, self.window_h / 2)
        def pythagorean_distance(pos):
            return sqrt((pos[0] - my_pos[0])**2 + (pos[1] - my_pos[1])**2)
        targets.sort(key=pythagorean_distance)
        # remove targets that are further away than SEARCH_RADIUS
        targets = [t for t in targets if pythagorean_distance(t) < self.SEARCH_RADIUS]
        return targets

        # checks if tooltip is there
    def confirm_tooltip(self, target_position):
        result = cv.matchTemplate(self.screenshot, self.mining_tooltip, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        if max_val >= self.TOOLTIP_MATCH_THRESHOLD:
            return True
        else:
            return False

        # determines if the character is moving or not
    def have_stopped_moving(self):
        if self.movement_screenshot is None:
            self.movement_screenshot = self.screenshot.copy()
            return False

        result = cv.matchTemplate(self.screenshot, self.movement_screenshot, cv.TM_CCOEFF_NORMED)
        similarity = result[0][0]

        if similarity >= self.MOVEMENT_STOPPED_THRESHOLD:
            return True

        self.movement_screenshot = self.screenshot.copy()
        return False

        # counts the items in inventory. This is done by checking if the place where the item is supposed to be is not empty
    def check_inventory(self):
        if self.item_count == 28:
            self.item_count = 0
            return True

        image = ImageGrab.grab()
        point = (self.window_w - 220, self.window_h - 303)
        point = self.get_screen_position(point)
        x, y = point
        x_iteration = 43
        y_iteration = 36
        items = 0
        
        for x_point in range(4):
            x += x_iteration
            y = point[1]
            for y_point in range(7):
                y += y_iteration
                color = image.getpixel((x, y))
                if color != (62, 53, 41):
                    items+=1
                else:
                    pass

        self.item_count = items
        return False

        # checks if the character is still in action by counting inventory. If item count has increased, it means that it is done. Also returns False if the action is taking too long
    def is_mining(self):
        items = self.item_count
        while(True):
            self.check_inventory()
            now = time()
            elapsed_time = now - self.timestamp
            if items < self.item_count:
                print(f"Items in inventory: {self.item_count}")
                return False
            elif elapsed_time > self.MAX_MINING_TIME:
                print(f"Time elapsed: {round(elapsed_time)}. Switching targets")
                return False
            else:
                return True

        # navigates using a file created by record_mouse_pos.py
    def navigate_to(self, destination):
        if self.stopped:
            return

        print(f"Following {destination} path")
        navigation = open(destination, 'r')

        coordinates = []

        for line in navigation:
            for word in line.split():
                coordinates.append(word)

        x_coordinates = coordinates[::3]
        y_coordinates = coordinates[1::3]
        time_required = coordinates[2::3]

        try:
            for x in range(len(x_coordinates)):
                point_x = int(float(x_coordinates[x]))
                point_y = int(float(y_coordinates[x]))
                sleep_time =  int(float(time_required[x]))
                sleep(sleep_time)
                pyautogui.click(point_x, point_y)
            sleep(8)
            return True
        except:
            return False

        # changes the mouse position depending on window offset
    def get_screen_position(self, pos):
        return (pos[0] + self.window_offset[0], pos[1] + self.window_offset[1])

        # self explanatory
    def update_targets(self, targets):
        self.lock.acquire()
        self.targets = targets
        self.lock.release()

    def update_screenshot(self, screenshot):
        self.lock.acquire()
        self.screenshot = screenshot
        self.lock.release()

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

        # this is the main logic controller
    def run(self):
        while not self.stopped:
            if self.state == BotState.INITIALIZING:
                if time() > self.timestamp + self.INITIALIZING_SECONDS:
                    self.lock.acquire()
                    self.state = BotState.SEARCHING
                    self.lock.release()

            elif self.state == BotState.SEARCHING:
                if self.item_count == 28:
                    self.lock.acquire()
                    self.state = BotState.STASHING
                    self.lock.release()
                else:
                    success = self.click_next_target()
                    if not success:
                        success = self.click_next_target()

                    if success:
                        self.lock.acquire()
                        self.state = BotState.MOVING
                        self.lock.release()
                    else:
                        pass

            elif self.state == BotState.MOVING:
                if not self.have_stopped_moving():
                    sleep(0.2)
                else:
                    self.lock.acquire()
                    self.timestamp = time()
                    self.state = BotState.MINING
                    self.lock.release()
                
            elif self.state == BotState.MINING:
                if not self.is_mining():
                    self.lock.acquire()
                    self.state = BotState.SEARCHING
                    self.lock.release()
                else:
                    pass

            elif self.state == BotState.STASHING:
                if self.check_inventory():
                    if self.navigate_to(self.STASHING_PATH):
                        self.lock.acquire()
                        self.state = BotState.SEARCHING
                        self.lock.release()
                else:
                    self.lock.acquire()
                    self.state = BotState.SEARCHING
                    self.lock.release()