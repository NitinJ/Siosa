import logging
from time import sleep

import pyautogui


class KeyboardController:
    def __init__(self, key_press_delay=0.01):
        """
        Args:
            key_press_delay:
        """
        self.key_press_delay = key_press_delay
        self.held_modifier_keys = {}
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')

    def __del__(self):
        self.unhold()

    def hold_modifier(self, key):
        """
        Args:
            key:
        """
        key = key.lower()
        if key in self.held_modifier_keys.keys():
            return
        sleep(self.key_press_delay)
        pyautogui.keyDown(key)
        self.held_modifier_keys[key] = 1

    def unhold_modifier(self, key):
        """
        Args:
            key:
        """
        key = key.lower()
        if key not in self.held_modifier_keys.keys():
            return False
        sleep(self.key_press_delay)
        pyautogui.keyUp(key)
        self.held_modifier_keys.pop(key)
        return True

    def keypress(self, key):
        """
        Args:
            key:
        """
        self.logger.debug(
            'Keypress: {} {}'.format("+".join(self.held_modifier_keys), key))
        sleep(self.key_press_delay)
        pyautogui.press(key)

    def keypress_with_modifiers(self, keys):
        """
        Args:
            keys:
        """
        pyautogui.hotkey(*keys, interval=self.key_press_delay)

    def write(self, text):
        """
        Args:
            text:
        """
        sleep(self.key_press_delay)
        pyautogui.write(text)

    def unhold(self):
        for k in self.held_modifier_keys.keys():
            sleep(self.key_press_delay)
            pyautogui.keyUp(k)
        self.held_modifier_keys.clear()

