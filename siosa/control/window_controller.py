# -*-coding:utf8-*-

import mss
import pywinauto as pwa
from win32api import MonitorFromWindow, GetMonitorInfo
from win32gui import GetWindowText, GetForegroundWindow

from siosa.common.singleton import Singleton


class WindowController(metaclass=Singleton):
    def __init__(self):
        self.app = pwa.application.Application()

        # TODO: What if it's not the first window ?
        self.app.connect(title='Path of Exile',
                         class_name='POEWindowClass', found_index=0)

        if not self.app.is_process_running():
            raise Exception("Path of Exile is not running")
        self.app_dialog = self.app.window()

        monitor = MonitorFromWindow(self.app_dialog.handle)
        # Monitor info is x1, y1, x2, y2
        monitor_info = GetMonitorInfo(monitor)
        self.monitor_dimensions = monitor_info['Monitor']
        self.mss_monitor = \
            WindowController._get_mss_monitor(self.monitor_dimensions)
        self.monitor_dimensions = (
            self.monitor_dimensions[0], self.monitor_dimensions[1],
            self.monitor_dimensions[2] - self.monitor_dimensions[0],
            self.monitor_dimensions[3] - self.monitor_dimensions[1])
        self.is_primary_monitor = monitor_info['Flags']

    def get_poe_monitor_dimensions(self):
        return self.monitor_dimensions

    def get_mss_monitor(self):
        return self.mss_monitor

    @staticmethod
    def _get_mss_monitor(monitor_dimensions):
        monitors = mss.mss().monitors
        for i, monitor in enumerate(monitors):
            if not i:
                # Real monitor list start from 1. 0 has dimensions for all the
                # monitors combined.
                continue
            if monitor_dimensions[0] == monitor['left'] and \
                    monitor_dimensions[1] == monitor['top'] and \
                    monitor_dimensions[2] == (monitor['left'] +
                                              monitor['width']) and \
                    monitor_dimensions[3] == (monitor['top'] +
                                              monitor['height']):
                return i
        return 1

    def move_to_poe(self):
        self.app_dialog.set_focus()

    def is_poe_in_foreground(self):
        return self.app_dialog.is_active()

    def is_poe_in_foreground2(self):
        return GetWindowText(GetForegroundWindow()) == 'Path of Exile'
