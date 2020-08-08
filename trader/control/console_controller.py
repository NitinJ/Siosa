from keyboard_controller import KeyboardController
from common.decorations import *

import pyautogui
import time

@singleton
class ConsoleController:
    def __init__(self, delay=0.05):
        self.keyboard_controller = KeyboardController()
        self.delay = delay
    
    def send_chat(self, to, chat):
        pyautogui.press('enter')
        time.sleep(self.delay)
        pyautogui.write('@{} {}'.format(to, chat))
        time.sleep(self.delay)
        pyautogui.press('enter')

    def console_command(self, command):
        pyautogui.press('enter')
        time.sleep(self.delay)
        pyautogui.write(command)
        time.sleep(self.delay)
        pyautogui.press('enter')