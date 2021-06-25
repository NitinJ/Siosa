import time

import pyautogui

from siosa.common.singleton import Singleton


class MouseController(metaclass=Singleton):
    TIME_BETWEEN_CLICKS = 0.01

    def __init__(self, location_factory, mouse_move_duration=0.2,
                 mouse_movement_curve=pyautogui.easeInOutQuad):
        self.location_factory = location_factory
        self.current_location = self.location_factory.create(0, 0, 0, 0)
        self.mouse_move_duration = mouse_move_duration
        self.mouse_movement_curve = mouse_movement_curve
        self.last_click_ts = None

    def move_mouse(self, location, mouse_move_duration=None):
        if location.equals(self.current_location):
            return
        point = location.get_center()
        duration = self.mouse_move_duration if not mouse_move_duration \
            else mouse_move_duration
        pyautogui.moveTo(point[0], point[1],
                         duration,
                         self.mouse_movement_curve)
        self.current_location = location

    def right_click(self):
        if self.last_click_ts:
            time.sleep(max(0,
                           MouseController.TIME_BETWEEN_CLICKS - time.time() - self.last_click_ts))
        pyautogui.click(button='right')
        self.last_click_ts = time.time()

    def click(self):
        if self.last_click_ts:
            time.sleep(max(0,
                           MouseController.TIME_BETWEEN_CLICKS - time.time() - self.last_click_ts))
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
