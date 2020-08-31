import logging
from time import sleep

import pyautogui


class KeyboardController:
    def __init__(self, key_press_delay=0.02):
        self.key_press_delay = key_press_delay
        self.held_modifier_keys = {}
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')

    def __del__(self):
        self.unhold()

    def hold_modifier(self, key):
        key = key.lower()
        if key in self.held_modifier_keys.keys():
            return
        sleep(self.key_press_delay)
        pyautogui.keyDown(key)
        self.held_modifier_keys[key] = 1

    def unhold_modifier(self, key):
        key = key.lower()
        if key not in self.held_modifier_keys.keys():
            return
        sleep(self.key_press_delay)
        pyautogui.keyUp(key)
        self.held_modifier_keys.pop(key)

    def keypress(self, key):
        self.logger.debug('keypress {} {}'.format("+".join(self.held_modifier_keys), key))
        sleep(self.key_press_delay)
        pyautogui.press(key)

    def unhold(self):
        for key in self.held_modifier_keys.keys():
            self.unhold_modifier(key)
