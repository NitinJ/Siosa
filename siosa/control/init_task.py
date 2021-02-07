import logging

from siosa.control.game_task import Task
from siosa.control.steps.change_zone_step import ChangeZone
from siosa.control.steps.clean_inventory_step import CleanInventory
from siosa.control.steps.close_all_windows_step import CloseAllWindows
from siosa.control.steps.locate_stash_step import LocateStashStep
from siosa.control.steps.open_stash_step import OpenStash
from siosa.control.steps.place_stash_step import PlaceStash
from siosa.control.steps.scan_inventory_step import ScanInventory
from siosa.control.steps.switch_to_game_step import SwitchToGame
from siosa.control.steps.wait_step import Wait
from siosa.data import zones


class InitTask(Task):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.steps = InitTask.get_steps()
        Task.__init__(self, 11, self.steps, name='InitTask')

    def _cleanup_internal(self):
        pass

    def _resume_internal(self):
        pass

    @staticmethod
    def get_steps():
        return [
            SwitchToGame(),
            CloseAllWindows(),
            # Go to a zone and back to make sure we are in the hideout.
            # TODO: figure out a way to know the current zone of the
            #  player, without changing it twice. Maybe we can read the
            #  log file in reverse and find the last zone event.
            # ChangeZone(zones.Zones.MENAGERIE),
            # ChangeZone(zones.Zones.HIDEOUT),
            # PlaceStash(),
            LocateStashStep(),
            OpenStash(),
            Wait(1),
            ScanInventory(),
            CleanInventory()
        ]
