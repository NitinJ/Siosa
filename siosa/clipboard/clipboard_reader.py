import win32clipboard
import logging

from siosa.common.singleton import Singleton


class ClipboardReader(Singleton):
    def __init__(self):
        Singleton.__init__(self)
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
                data = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                return data
            except Exception as e:
                self.logger.error("Error while reading clipboard: {}".format(str(e)))
                

    def _write_internal(self, data):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(data)
        win32clipboard.CloseClipboard()
