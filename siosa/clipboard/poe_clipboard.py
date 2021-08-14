import logging
import time

from siosa.clipboard.clipboard_reader import ClipboardReader, \
    ClipboardDataFormatException
from siosa.control.keyboard_controller import KeyboardController
from siosa.data.poe_item_factory import PoeItemFactory


class PoeClipboard:
    COPY_KEY_COMBINATION = ['ctrl', 'alt', 'c']

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')

        self.clipboard_reader = ClipboardReader()
        self.keyboard_controller = KeyboardController()
        self.item_factory = PoeItemFactory()

    def read_item_at_cursor(self):
        self.logger.debug("Reading item at cursor")
        self.keyboard_controller.keypress_with_modifiers(
            PoeClipboard.COPY_KEY_COMBINATION)

        try:
            data = self.clipboard_reader.get_clipboard_data()
            if not data:
                self.logger.debug("Clipboard data is none")
                return None
            return self.item_factory.get_item(data)
        except ClipboardDataFormatException as e:
            self.logger.debug("Clipboard format data exception: {}".format(e))
            time.sleep(0.05)
            return self.read_item_at_cursor()
