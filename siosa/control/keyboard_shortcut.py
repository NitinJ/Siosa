import logging

import keyboard


class KeyboardShortcut:
    def __init__(self, combination, callback):
        """
        Args:
            combination:
            callback:
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.callback = callback
        self.combination = combination
        keyboard.add_hotkey(combination, self.on_activate)
        self.logger.info("Registered keyboard shortcut for {}".format(
            self.combination))

    def on_activate(self):
        self.logger.info("Shortcut activated for {}".format(self.combination))
        self.callback()
