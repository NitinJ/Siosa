# -*-coding:utf8-*-
import time

import pywinauto as pwa
from win32gui import GetWindowText, GetForegroundWindow
from siosa.common.singleton import Singleton


class WindowController(metaclass=Singleton):
    def __init__(self):
        self.app = pwa.application.Application()

        # TODO: What if it's not the first window ?
        self.app.connect(title_re='Path of Exile', found_index=0)

        if not self.app.is_process_running():
            raise Exception("Path of Exile is not running")
        self.app_dialog = self.app.window()

    def move_to_poe(self):
        self.app_dialog.set_focus()

    def is_poe_in_foreground(self):
        return self.app_dialog.is_active()

    def is_poe_in_foreground2(self):
        return GetWindowText(GetForegroundWindow()) == 'Path of Exile'
