import logging
import time

from siosa.control.game_step import Step
from siosa.control.game_task import Task
from siosa.control.steps.change_zone_step import ChangeZone
from siosa.control.steps.close_all_windows_step import CloseAllWindows
from siosa.control.steps.open_stash_step import OpenStash
from siosa.control.steps.place_stash_step import PlaceStash
from siosa.control.steps.scan_inventory_step import ScanInventory
from siosa.control.steps.test_step import TestStep
from siosa.control.steps.switch_to_game_step import SwitchToGame
from siosa.data import zones


class InitTask(Task):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.steps = InitTask.get_steps()
        Task.__init__(self, 11, self.steps, name='InitTask')

    def cleanup(self):
        pass

    def resume(self, game_state):
        self.game_state = game_state
        pass

    @staticmethod
    def get_steps():
        return [
            SwitchToGame(),
            # CloseAllWindows(game_state),
            # ChangeZone(game_state, zones.Zones.HIDEOUT),
            # PlaceStash(game_state),
            # OpenStash(game_state),
            # ScanInventory(game_state)
            # TestStep(game_state)
        ]
