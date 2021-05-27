import time

import win32clipboard


class Clipboard:
    def __init__(self, clipboard_read_sleep_time=0.15):
        self.clipboard_read_sleep_time = clipboard_read_sleep_time

    def set_clipboard_data(self, data):
        try:
            win32clipboard.OpenClipboard()
        except:
            time.sleep(self.clipboard_read_sleep_time)
            win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(data)
        win32clipboard.CloseClipboard()

    def get_clipboard_data(self):
        try:
            win32clipboard.OpenClipboard()
        except:
            time.sleep(self.clipboard_read_sleep_time)
            win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        self.set_clipboard_data('')
        return data.lower()
