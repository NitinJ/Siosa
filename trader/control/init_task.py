import logging 
import time

from game_task import Task
from game_step import *
from data import zones

class InitTask(Task):
    def __init__(self, game_state):
        self.logger = logging.getLogger(__name__)
        self.steps = InitTask.get_steps(game_state)
        Task.__init__(self, game_state, 11, self.steps, name='InitTask')

    def cleanup(self):
        pass

    def resume(self):
        pass

    @staticmethod
    def get_steps(game_state):
        return [
            SwitchToGame(game_state),
            CloseAllWindows(game_state),
            ChangeZone(game_state, zones.Zones.HIDEOUT),
            PlaceStash(game_state),
            OpenStash(game_state),
            ScanInventory(game_state)
        ]