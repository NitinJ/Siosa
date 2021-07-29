import logging

from siosa.control.game_task import Task
from siosa.control.steps.change_stash_tab_step import ChangeStashTab
from siosa.control.steps.clean_inventory_step import CleanInventory
from siosa.control.steps.close_all_windows_step import CloseAllWindows
from siosa.control.steps.open_stash_step import OpenStash
from siosa.control.steps.scan_inventory_step import ScanInventory
from siosa.control.steps.switch_to_game_step import SwitchToGame
from siosa.control.steps.wait_step import Wait


class InitTask(Task):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        Task.__init__(self, 11, name='InitTask')

    def get_steps(self):
        return (
            SwitchToGame(),
            CloseAllWindows(),
            OpenStash(),
            Wait(1),
            ChangeStashTab(0),
            ScanInventory(),
            CleanInventory()
        )
