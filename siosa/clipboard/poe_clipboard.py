import logging

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
        self.logger.debug("Reading data from clipboard")
        self.keyboard_controller.keypress_with_modifiers(
            PoeClipboard.COPY_KEY_COMBINATION)

        try:
            return self.item_factory.get_item(
                self.clipboard_reader.get_clipboard_data())
        except ClipboardDataFormatException as e:
            self.keyboard_controller.keypress_with_modifiers(
                PoeClipboard.COPY_KEY_COMBINATION)
            try:
                return self.item_factory.get_item(
                    self.clipboard_reader.get_clipboard_data())
            except:
                return None
