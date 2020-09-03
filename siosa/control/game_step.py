import logging

from siosa.common.decorations import abstractmethod
from siosa.control.console_controller import ConsoleController
from siosa.control.keyboard_controller import KeyboardController
from siosa.control.mouse_controller import MouseController
from siosa.control.window_controller import WindowController
from siosa.location.location_factory import LocationFactory


class Step:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.game_state = None
        self.kc = KeyboardController()
        self.lf = LocationFactory()
        self.mc = MouseController(self.lf)
        self.cc = ConsoleController()
        self.wc = WindowController()

    @abstractmethod
    def execute(self, game_state):
        pass
