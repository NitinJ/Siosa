import math
import time

import pyautogui

from siosa.common.singleton import Singleton
from siosa.location.location_factory import LocationFactory


class MouseController(metaclass=Singleton):
    TIME_BETWEEN_CLICKS = 0.1
    def __init__(self, location_factory, mouse_move_duration=0.3, mouse_movement_curve=pyautogui.easeInOutQuad):
        self.location_factory = location_factory
        self.current_location = self.location_factory.create(0, 0, 0, 0)
        self.mouse_move_duration = mouse_move_duration
        self.mouse_movement_curve = mouse_movement_curve
        self.last_click_ts = None

    def move_mouse(self, location):
        if location.equals(self.current_location):
            return
        point = location.get_random_point()
        pyautogui.moveTo(point[0], point[1], self.mouse_move_duration, self.mouse_movement_curve)
        self.current_location = location

    def right_click(self):
        if self.last_click_ts: 
            time.sleep(max(0, MouseController.TIME_BETWEEN_CLICKS - time.time() - self.last_click_ts))
        pyautogui.click(button='right')
        self.last_click_ts = time.time()

    def click(self):
        if self.last_click_ts: 
            time.sleep(max(0, MouseController.TIME_BETWEEN_CLICKS - time.time() - self.last_click_ts))
        pyautogui.click(button='left')
        self.last_click_ts = time.time()

    def get_current_location(self):
        return self.current_location

    def move_to_screen_center(self):
        self.move_mouse(self.location_factory.get_center_of_screen())

    def click_at_location(self, location, click='left'):
        self.move_mouse(location)
        if click == 'left':
            self.click()
        else:
            self.right_click()

if __name__ == "__main__":
    location_factory = LocationFactory()
    mc = MouseController(location_factory)
    mc.move_mouse(location_factory.create(302, 34, 302, 34))
