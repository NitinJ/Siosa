import logging

from siosa.control.game_step import Step, StepStatus
from siosa.control.game_task import Task
from siosa.control.steps.locate_stash_step import LocateStashStep
from siosa.control.steps.switch_to_game_step import SwitchToGame
from siosa.location.location_factory import Locations


class FakeInitTask(Task):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        Task.__init__(self, 11, name='InitTask')

    def get_steps(self):
        return (
            SwitchToGame(),
            LocateStashStep(),
            FakeStep()
        )


class FakeStep(Step):
    def execute(self, game_state):
        """
        Args:
            game_state:
        """
        game_state.update(
            {'stash_location': self.lf.get(Locations.SCREEN_CENTER)})
        game_state.update({'stash_open': True})
        return StepStatus(True)
