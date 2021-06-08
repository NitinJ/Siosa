import time

import pyautogui

from tools.roller.singleton import Singleton


class KMController(metaclass=Singleton):
    def __init__(self, key_press_delay=0.005, mouse_move_delay=0.010):
        self.down_keys = {}
        self.key_press_delay = key_press_delay
        self.mouse_move_delay = mouse_move_delay
        self.current_location = None

    def copy_item_at_cursor(self):
        self.key_down('ctrl')
        self.key_down('altleft')
        pyautogui.press('c')
        self.key_up('altleft')
        self.key_up('ctrl')

    def move_mouse(self, location):
        if self.current_location == location:
            return
        x1, y1, x2, y2 = location
        x = (x1 + x2) // 2
        y = (y1 + y2) // 2
        pyautogui.moveTo(x, y, self.mouse_move_delay, pyautogui.easeInOutQuad)
        self.current_location = location
        return

    def click(self, button='left'):
        pyautogui.click(button=button)

    def key_down(self, x):
        if x in self.down_keys.keys():
            return
        time.sleep(self.key_press_delay)
        self.down_keys[x] = True
        pyautogui.keyDown(x)

    def key_up(self, x):
        if x not in self.down_keys.keys():
            return
        time.sleep(self.key_press_delay)
        del self.down_keys[x]
        pyautogui.keyUp(x)

    def all_keys_up(self):
        for k in self.down_keys.keys():
            time.sleep(self.key_press_delay)
            pyautogui.keyUp(k)
        self.down_keys.clear()