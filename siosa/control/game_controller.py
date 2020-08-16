import logging
import time
from enum import Enum

from siosa.common.singleton import Singleton
from siosa.control.console_controller import ConsoleController
from siosa.control.game_state import GameState
from siosa.control.game_state_updater import (PlayerInHideoutUpdater,
                                              ZoneUpdater)
from siosa.control.init_task import InitTask
from siosa.control.window_controller import WindowController
from siosa.data.zones import Zones


class GameController(metaclass=Singleton):
    def __init__(self, client_log_listener):
        super(GameController, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.log_listener = client_log_listener
        self.game_state = GameState()
        self.game_state_updaters = [
            PlayerInHideoutUpdater(self.game_state, self.log_listener),
            ZoneUpdater(self.game_state, self.log_listener)
        ]
        self.wc = WindowController()
        self.cc = ConsoleController()       
        self.running_task = None
        self.not_running_tasks = []

        self._start_game_state_updaters()
        self._initialize()

    def _start_game_state_updaters(self):
        for updater in self.game_state_updaters:
            updater.start()
            
    def _initialize(self):
        self.submit_task(InitTask(self.game_state))

    def submit_task(self, task):
        self.logger.debug("New task submitted: {}".format(task.name))
        if not self.running_task or not self.running_task.is_alive():
            self.not_running_tasks.append(task)
        task_with_max_priority = {
            'priority': 0,
            'task': None
        }
        for i in range(0, len(self.not_running_tasks)):
            _task = self.not_running_tasks[i]
            if _task.priority > task_with_max_priority['priority']:
                task_with_max_priority = {
                    'priority': _task.priority,
                    'task': _task
                }
        self.running_task = task_with_max_priority['task']
        self.running_task.start()
