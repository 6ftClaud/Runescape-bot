import cv2 as cv
import pyautogui
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
    MINING_SECONDS = 3
    MOVEMENT_STOPPED_THRESHOLD = 0.9
    TOOLTIP_MATCH_THRESHOLD = 0.7
    IGNORE_RADIUS = 200
    MAX_MINING_TIME = 8
    BANK = 'images/bank.png'
    MINE = 'images/mine.png'
    CURRENT_POSITION = 'images/current_position.png'

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
        print("Initializing bot")
        self.timestamp = time()

    def click_next_target(self):
        targets = self.targets_ordered_by_distance(self.targets)
        items = self.item_count
        target_i = 0
        found_copper = False

        while not found_copper and target_i < len(targets):
            if self.stopped:
                break

            target_pos = targets[target_i]
            screen_x, screen_y = self.get_screen_position(target_pos)
            pyautogui.moveTo(x=screen_x, y=screen_y)
            sleep(0.1)

            if self.confirm_tooltip(target_pos):
                print('Mining at x:{} y:{}'.format(screen_x, screen_y))
                found_copper = True
                pyautogui.click(button='right')
                sleep(0.1)
                pyautogui.click(x=screen_x, y=screen_y + 25)
                start = time()

                while(True):
                    self.check_inventory()
                    now = time()
                    elapsed_time = now - start
                    if items < self.item_count:
                        print(f"Items in inventory: {self.item_count}")
                        return found_copper
                    elif elapsed_time > self.MAX_MINING_TIME:
                        print(f" Time elapsed: {elapsed_time}. Switching targets")
                        break

            elif self.item_count == 28:
                break
            elif not self.confirm_tooltip(target_pos):
                del targets[target_i]
            elif targets is None:
                self.update_targets(targets)

            target_i += 1

    def targets_ordered_by_distance(self, targets):
        redundant_targets = []
        my_pos = (self.window_w / 2, self.window_h / 2)
        def pythagorean_distance(pos):
            return sqrt((pos[0] - my_pos[0])**2 + (pos[1] - my_pos[1])**2)
        targets.sort(key=pythagorean_distance)
        redundant_targets = targets
        # remove targets that are further away than IGNORE_RADIUS
        redundant_targets = [t for t in redundant_targets if pythagorean_distance(t) < self.IGNORE_RADIUS]
        # if there are no targets in range of IGNORE_RADIUS, return 'targets'
        if not redundant_targets:
            return targets
        else:
            return redundant_targets

    def confirm_tooltip(self, target_position):
        result = cv.matchTemplate(self.screenshot, self.mining_tooltip, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        if max_val >= self.TOOLTIP_MATCH_THRESHOLD:
            return True
        else:
            return False

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

    def check_inventory(self):
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
                if not pyautogui.pixelMatchesColor(round(x), round(y), (62, 53, 41)) or pyautogui.pixelMatchesColor(round(x), round(y), (0, 0, 1)):
                    items+=1
                else:
                    pass

        if self.item_count == 28:
            self.item_count = 0
            return True
        else:
            self.item_count = items
            return False

    def navigate_to(self, location, destination):
        world_map = ((self.window_w - 25, 147))
        world_map = self.get_screen_position(world_map)
        pyautogui.click(world_map[0], world_map[1])
        sleep(5)
        x_current, y_current = pyautogui.locateCenterOnScreen(location, confidence=0.3)
        x_destination, y_destination = pyautogui.locateCenterOnScreen(location, confidence=0.3)
        x = self.window_w - 85
        y = 100

        while True:
            try:
                x_current, y_current = pyautogui.locateCenterOnScreen(location, confidence=0.3)
                x_destination, y_destination = pyautogui.locateCenterOnScreen(location, confidence=0.3)
            except:
                continue
            if y_current > y_destination:
                pyautogui.click(x, y - 30)
            elif y_current < y_destination:
                pyautogui.click(x, y + 30)
            elif (y_current - y_destination) < 10:
                break
            else:
                break
        while True:
            try:
                x_current, y_current = pyautogui.locateCenterOnScreen(location, confidence=0.75)
                x_destination, y_destination = pyautogui.locateCenterOnScreen(location, confidence=0.75)
            except:
                continue
            if x_current > x_destination:
                pyautogui.click(x - 30, y)
            elif x_current < x_destination:
                pyautogui.click(x + 30, y)
            elif (x_current - x_destination) < 10:
                break
            else:
                break


    def get_screen_position(self, pos):
        return (pos[0] + self.window_offset[0], pos[1] + self.window_offset[1])


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

    def run(self):
        while not self.stopped:
            if self.state == BotState.INITIALIZING:
                if time() > self.timestamp + self.INITIALIZING_SECONDS:
                    self.lock.acquire()
                    self.state = BotState.SEARCHING
                    print("Searching for ore")
                    self.lock.release()

            elif self.state == BotState.SEARCHING:
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
                    sleep(0.500)
                else:
                    self.lock.acquire()
                    if self.state == BotState.MOVING:
                        self.timestamp = time()
                        self.state = BotState.MINING
                    self.lock.release()
                
            elif self.state == BotState.MINING:
                if self.item_count == 28:
                    self.lock.acquire()
                    self.state = BotState.STASHING
                    print("Going to bank")
                    self.lock.release()
                elif time() > self.timestamp + self.MINING_SECONDS:
                    self.lock.acquire()
                    self.state = BotState.SEARCHING
                    print("Searching for ore")
                    self.lock.release()

            elif self.state == BotState.STASHING:
                if not self.check_inventory():
                    self.lock.acquire()
                    self.state = BotState.SEARCHING
                    print("Searching for ore")
                    self.lock.release()
                