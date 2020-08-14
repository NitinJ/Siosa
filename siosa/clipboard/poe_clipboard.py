import logging

from siosa.clipboard.clipboard_reader import ClipboardReader
from siosa.control.keyboard_controller import KeyboardController
from siosa.data.poe_item_factory import PoeItemFactory

class PoeClipboard:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')

        self.clipboard_reader = ClipboardReader.get_instance()
        self.keyboard_controller = KeyboardController()
        self.item_factory = PoeItemFactory()

    def read_item_at_cursor(self):
        self.logger.debug("Reading data from clipboard")

        self.keyboard_controller.hold_modifier('ctrl')
        self.keyboard_controller.keypress('c')
        self.keyboard_controller.unhold_modifier('ctrl')
        data = self.clipboard_reader.get_clipboard_data()
        return self.item_factory.get_item(data)