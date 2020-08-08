import logging

from clipboard_reader import ClipboardReader


class PoeClipboard:
    def __init__(self, keyboard_controller, item_factory):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')

        self.clipboard_reader = ClipboardReader()
        self.keyboard_controller = keyboard_controller
        self.item_factory = item_factory

    def read_item_at_cursor(self):
        self.logger.debug("Reading data from clipboard")

        self.keyboard_controller.hold_modifier('ctrl')
        self.keyboard_controller.keypress('c')
        self.keyboard_controller.unhold_modifier('ctrl')
        data = self.clipboard_reader.get_clipboard_data()
        return self.item_factory.get_item(data)