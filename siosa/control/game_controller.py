import logging

from siosa.common.singleton import Singleton
from siosa.control.game_state import GameState
from siosa.control.game_state_updater import (PlayerInHideoutUpdater,
                                              ZoneUpdater)
from siosa.control.game_task_executor import GameTaskExecutor
from siosa.control.init_task import InitTask


class GameController(metaclass=Singleton):
    def __init__(self, client_log_listener):
        super(GameController, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.game_state = GameState()
        self.task_executor = GameTaskExecutor(self.game_state)
        self.task_executor.start()

        self.log_listener = client_log_listener
        self.game_state_updaters = [
            PlayerInHideoutUpdater(self.game_state, self.log_listener),
            ZoneUpdater(self.game_state, self.log_listener)
        ]
        self._start_game_state_updaters()
        self._initialize()

    def _start_game_state_updaters(self):
        for updater in self.game_state_updaters:
            updater.start()

    def _initialize(self):
        # self.submit_task(FakeInitTask())
        self.submit_task(InitTask())

    def submit_task(self, task):
        self.task_executor.submit_task(task)
