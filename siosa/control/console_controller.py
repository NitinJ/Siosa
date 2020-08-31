import time

import pyautogui

from siosa.common.singleton import Singleton
from siosa.control.keyboard_controller import KeyboardController


class ConsoleController(metaclass=Singleton):
    # Time after which console is cleared after issuing any command. This is
    # done so that command and console messages don't interfare between image
    # parsing done in the app.
    CONSOLE_CLEAR_DELAY = 1.0
    
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
        self._clear()
    
    def clear_console(self):
        self._clear()
        
    def _clear(self):
        pyautogui.press('enter')
        time.sleep(ConsoleController.CONSOLE_CLEAR_DELAY)
        pyautogui.write("/clear")
        time.sleep(self.delay)
        pyautogui.press('enter')
