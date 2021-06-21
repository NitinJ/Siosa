import logging

from siosa.common.decorations import abstractmethod
from siosa.control.console_controller import ConsoleController
from siosa.control.keyboard_controller import KeyboardController
from siosa.control.mouse_controller import MouseController
from siosa.control.window_controller import WindowController
from siosa.location.location_factory import LocationFactory


class StepStatus:
    """
    Status of a Step's execution.
    """

    def __init__(self, success, info={}):
        self.success = success
        self.info = info

    def __repr__(self):
        return "Success: {}, info: {}".format(self.success, self.info)


class Step:
    """
    Step is the smallest unit of work inside the game. Steps are supposed to be
    highly reusable, preferably small units. Steps return the status of the
    execution via the step status object. Steps are executed at a given
    GameState.
    """

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
    def execute(self, game_state) -> StepStatus:
        """
        Executes the step and returns the status of execution.
        Args:
            game_state: The game state object.

        Returns: Status of the execution.
        """
        pass
