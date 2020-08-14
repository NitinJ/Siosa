#-*-coding:utf8-*-
import time

import pywinauto as pwa
import pywinauto.handleprops as _handleprops
import pywinauto.win32functions as _win32functions

from win32gui import GetForegroundWindow, GetWindowText


class WindowController:
    def __init__(self):
        self.app = pwa.application.Application()
        self.app.connect(title_re='Path of Exile')

    def move_to_poe(self):
        if not self.app.is_process_running():
            raise Exception("Path of Exile is not running")
        app_dialog = self.app.window()
        app_dialog.set_focus()

    @staticmethod
    def is_poe_in_foreground():
        return GetWindowText(GetForegroundWindow()) == 'Path of Exile'

if __name__ == "__main__":
    for i in xrange(0, 15):
        print WindowController.is_poe_in_foreground()
        time.sleep(0.1)
    wc = WindowController()
    wc.move_to_poe()
