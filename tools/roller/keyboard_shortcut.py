import logging

from pynput import keyboard


class KeyboardShortcut:
    def __init__(self, combination, callback):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.combination = combination
        self.current_key_set = set()
        self.callback = callback
        hotkey = keyboard.HotKey(
            keyboard.HotKey.parse(self.combination),
            self.on_activate)
        self.listener = keyboard.Listener(
            on_press=self.for_canonical(hotkey.press),
            on_release=self.for_canonical(hotkey.release))

    def for_canonical(self, f):
        return lambda k: f(self.listener.canonical(k))

    def start_listening(self):
        self.listener.start()
        self.logger.info("Started listening to keyboard shortcut.")

    def on_activate(self):
        self.callback()