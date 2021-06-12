import logging

from siosa.common.singleton import Singleton
from siosa.control.game_state import GameState
from siosa.control.game_state_updater import (PlayerInHideoutUpdater,
                                              ZoneUpdater)
from siosa.control.game_task_executor import GameTaskExecutor
from siosa.control.init_task import InitTask
from siosa.control.keyboard_shortcut import KeyboardShortcut


class GameController(metaclass=Singleton):
    TASK_STOP_COMBINATION = "ctrl+q"

    def __init__(self, client_log_listener):
        super(GameController, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.game_state = GameState()
        self.task_executor = GameTaskExecutor(self.game_state)

        self.keyboard_listener = KeyboardShortcut(
            GameController.TASK_STOP_COMBINATION, self._stop_all_tasks)
        self.log_listener = client_log_listener
        self.game_state_updaters = [
            PlayerInHideoutUpdater(self.game_state, self.log_listener),
            ZoneUpdater(self.game_state, self.log_listener)
        ]
        # Start threads
        self.task_executor.start()
        self._start_game_state_updaters()
        self._initialize()

    def _start_game_state_updaters(self):
        for updater in self.game_state_updaters:
            self.logger.debug("Starting game state updater: {}".format(updater))
            updater.start()

    def _initialize(self):
        # self.submit_task(FakeInitTask())
        self.submit_task(InitTask())

    def submit_task(self, task):
        self.task_executor.submit_task(task)

    def _stop_all_tasks(self):
        self.task_executor.stop_all_tasks()
