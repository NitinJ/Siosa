import logging
import time

import win32clipboard

from siosa.common.singleton import Singleton


class ClipboardDataFormatException(Exception):
    def __init__(self):
        super().__init__()


class ClipboardReader(metaclass=Singleton):
    FORMAT_ERROR = "Specified clipboard format is not available"

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self.last_read_data = None
        self.last_write_data = None
        self.previously_written_data = None

    def set_clipboard_data(self, data):
        self.previously_written_data = self._read_internal()
        self._write_internal(data)
        self.last_write_data = data

    def get_clipboard_data(self):
        # get clipboard data
        data = self._read_internal()
        self.last_read_data = data
        self._write_internal('')
        return data

    def _read_internal(self):
        while True:
            try:
                win32clipboard.OpenClipboard()
                data = win32clipboard.GetClipboardData(
                    win32clipboard.CF_UNICODETEXT)
                win32clipboard.CloseClipboard()
                return data
            except RuntimeError as e:
                self.logger.error(
                    "Error while reading clipboard: {}".format(str(e)))
                if ClipboardReader.FORMAT_ERROR in str(e):
                    raise ClipboardDataFormatException()
            time.sleep(0.05)

    def _write_internal(self, data):
        while True:
            try:
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(data)
                win32clipboard.CloseClipboard()
                return
            except Exception as e:
                self.logger.error(
                    "Error while writing to clipboard: {}".format(str(e)))
            time.sleep(0.01)
