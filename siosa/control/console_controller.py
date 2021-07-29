import logging
import time
from enum import Enum

import pyautogui
import pyperclip

from siosa.common.singleton import Singleton
from siosa.control.keyboard_controller import KeyboardController


class ConsoleController(metaclass=Singleton):
    # Time after which console is cleared after issuing any command. This is
    # done so that command and console messages don't interfare between image
    # parsing done in the app.
    CONSOLE_CLEAR_DELAY = 1.0
    CONSOLE_SPAWN_DELAY = 0.25


    def __init__(self, delay=CONSOLE_SPAWN_DELAY):
        """
        Args:
            delay:
        """
        self.keyboard_controller = KeyboardController()
        self.delay = delay
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    def send_chat(self, to, chat):
        """
        Args:
            to:
            chat:
        """
        pyautogui.press('enter')
        time.sleep(self.delay)

        if not to.isascii():
            pyautogui.write('@')
            pyperclip.copy(to)
            pyautogui.hotkey("ctrl", "v")
            pyautogui.write(' {}'.format(chat))
        else:
            pyautogui.write('@{} {}'.format(to, chat))

        time.sleep(self.delay)
        pyautogui.press('enter')

    def console_command(self, command):
        """
        Args:
            command:
        """
        pyautogui.press('enter')
        time.sleep(self.delay)
        pyautogui.write(command)
        time.sleep(self.delay)
        pyautogui.press('enter')

    def clear_console(self):
        self._clear()

    def _clear(self):
        pyautogui.press('enter')
        time.sleep(self.delay)
        pyautogui.write('/clear')
        time.sleep(self.delay)
        pyautogui.press('enter')


class Commands:
    INVITE_TO_PARTY = (lambda x: "/invite {}".format(x))
    TRADE = (lambda x: "/tradewith {}".format(x))
    KICK_FROM_PARTY = (lambda x: "/kick {}".format(x))
    CLEAR = "/clear"


if __name__ == "__main__":
    cc = ConsoleController()
    cc.send_chat('@ыфвпуфкап', 'hey still want the gem ?')