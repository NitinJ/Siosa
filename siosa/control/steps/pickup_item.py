import time
from enum import Enum

from siosa.control.game_step import Step, StepStatus
from siosa.control.steps.change_stash_tab_step import ChangeStashTab
from siosa.data.stash_item import StashItem


class Error(Enum):
    ITEM_NOT_FOUND_IN_STASH = 0


class PickupItem(Step):
    # TODO: Remove this wait time and have a better mechanism to detect if stash
    # has loaded on screen.
    STASH_LOAD_WAIT_TIME = 1

    def __init__(self, stash_item: StashItem):
        """
        Args:
            stash_item (StashItem):
        """
        Step.__init__(self)
        self.stash_item = stash_item

    def execute(self, game_state):
        """
        Args:
            game_state:
        """
        self.game_state = game_state

        ChangeStashTab(self.stash_item.stash_tab.index).execute(game_state)

        # Stash sometimes takes a lot of time to load.
        time.sleep(PickupItem.STASH_LOAD_WAIT_TIME)

        if not self.stash_item.stash_tab.is_item_at_location_ingame(
                self.stash_item.position):
            return StepStatus(False, Error.ITEM_NOT_FOUND_IN_STASH)

        cell = list(self.stash_item.position).copy()
        item_position_xy = self.stash_item.stash_tab.get_cell_location(cell)
        self.mc.move_mouse(item_position_xy)
        self.kc.hold_modifier('Ctrl')
        self.mc.click()
        self.kc.unhold_modifier('Ctrl')
        ChangeStashTab(0).execute(game_state)
        return StepStatus(True)
