#-*-coding:utf8-*-
import time

import pywinauto as pwa
from win32gui import GetForegroundWindow, GetWindowText


class WindowController:
    def __init__(self):
        self.app = pwa.application.Application()

    def move_to_poe(self):
        self.app.connect(title_re='Path of Exile')
        if not self.app.is_process_running():
            raise Exception("Path of Exile is not running")
        app_dialog = self.app.window()
        app_dialog.set_focus()

    @staticmethod
    def is_poe_in_foreground():
        return GetWindowText(GetForegroundWindow()) == 'Path of Exile'

if __name__ == "__main__":
    for i in range(0, 15):
        print(WindowController.is_poe_in_foreground())
        time.sleep(0.1)
    wc = WindowController()
    wc.move_to_poe()
