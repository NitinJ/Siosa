import time
from enum import Enum

from siosa.clipboard.poe_clipboard import PoeClipboard
from siosa.control.game_step import Step, StepStatus
from siosa.control.steps.change_stash_tab_step import ChangeStashTab
from siosa.data.inventory import Inventory
from siosa.data.poe_item_factory import PoeItemFactory
from siosa.data.stash_item import StashItem
from siosa.location.location_factory import Locations


class Error(Enum):
    ITEM_NOT_FOUND_IN_INVENTORY = 0
    STASH_NOT_OPEN = 1
    COULD_NOT_MOVE_ITEM = 2


class PickupInventoryItem(Step):
    def __init__(self, inventory_location):
        """
        Args:
            stash_item (StashItem):
        """
        Step.__init__(self)
        self.inventory_location = inventory_location
        self.clipboard = PoeClipboard()

    def execute(self, game_state):
        """
        Args:
            game_state:
        """
        self.game_state = game_state.get()
        if not self.game_state['stash_open']:
            return StepStatus(False, Error.STASH_NOT_OPEN)

        self.mc.move_mouse(Inventory.get_location(self.inventory_location))
        item = self.clipboard.read_item_at_cursor()
        if not item:
            return StepStatus(False, Error.ITEM_NOT_FOUND_IN_INVENTORY)
        self.kc.hold_modifier('ctrl')
        self.mc.click()
        self.kc.unhold_modifier('ctrl')

        self.mc.move_mouse(self.lf.get(Locations.ITEM_LOCATION))
        item = self.clipboard.read_item_at_cursor()
        if not item:
            return StepStatus(False, Error.COULD_NOT_MOVE_ITEM)
        return StepStatus(True)
