import logging

from siosa.common.decorations import abstractmethod
from siosa.control.console_controller import ConsoleController
from siosa.control.keyboard_controller import KeyboardController
from siosa.control.mouse_controller import MouseController
from siosa.control.window_controller import WindowController
from siosa.location.location_factory import LocationFactory, Locations


class Step:
    def __init__(self, game_state):
        self.logger = logging.getLogger(__name__)
        self.game_state = game_state
        self.kc = KeyboardController()
        self.mc = MouseController(LocationFactory())
        self.cc = ConsoleController()
        self.wc = WindowController()

    @abstractmethod
    def execute(self):
        pass
