import logging 
import time

from game_task import Task
from game_step import OpenStash, SwitchToGame, ChangeZone, Wait
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
            OpenStash(game_state),
            ChangeZone(game_state, zones.Zones.METAMORPH),
            Wait(game_state, 2),
            ChangeZone(game_state, zones.Zones.HIDEOUT)
        ]