from enum import Enum

from siosa.clipboard.poe_clipboard import PoeClipboard
from siosa.control.game_step import Step, StepStatus
from siosa.data.inventory import Inventory
from siosa.data.stash import Stash
from siosa.location.location_factory import Locations


class Error(Enum):
    STASH_NOT_OPEN = 0
    ITEM_NOT_FOUND_IN_INVENTORY_CELL = 1
    STASH_TAB_NOT_OPEN = 2
    ITEM_ALREADY_EXISTS_IN_STASH = 3
    COULD_NOT_PLACE_ITEM_IN_STASH = 4
    ITEM_DIMENSIONS_UNKNOWN = 5


class PlaceItem(Step):
    def __init__(self, stash_index, stash_cell, item_cell):
        """
        Args:
            stash_index:
            stash_cell:
            item_cell:
        """
        Step.__init__(self)
        self.stash_index = stash_index
        self.stash_cell = stash_cell
        self.stash_tab = Stash().get_stash_tab_by_index(stash_index)
        assert self.stash_tab is not None

        self.item_cell = item_cell
        assert Inventory.is_in_bounds(item_cell)

        self.poe_clipboard = PoeClipboard()

    def execute(self, game_state):
        """
        Args:
            game_state:
        """
        self.game_state = game_state.get()
        if not self.game_state['stash_open']:
            return StepStatus(False, Error.STASH_NOT_OPEN)

        if self.game_state['open_stash_tab_index'] != self.stash_index:
            return StepStatus(False, Error.STASH_TAB_NOT_OPEN)

        if self.stash_tab.is_item_at_location_ingame(self.stash_cell):
            return StepStatus(False, Error.ITEM_ALREADY_EXISTS_IN_STASH)

        item = Inventory.get_item_at_cell(self.item_cell)
        if not item:
            return StepStatus(False, Error.ITEM_NOT_FOUND_IN_INVENTORY_CELL)
        w, h = item.get_dimensions()
        if not w or not h:
            item = \
                Inventory.get_item_at_cell(self.item_cell, get_dimensions=True)
        w, h = item.get_dimensions()
        if not w or not h:
            return StepStatus(False, Error.ITEM_DIMENSIONS_UNKNOWN)

        # Pickup item from cell.
        self.mc.move_mouse(Inventory.get_location(self.item_cell))
        self.mc.click()

        # Move to location in the stash tab.
        location = self.stash_tab.get_cell_location_for_placing_item(
            self.stash_cell, item.get_dimensions())
        self.mc.move_mouse(location)
        self.mc.click()
        self.mc.move_mouse(self.lf.get(Locations.SCREEN_NOOP_POSITION))

        if not self.stash_tab.is_item_at_location_ingame(self.stash_cell):
            # Somehow the item isn't in the stash tab, so place it back where we
            # picked it up from.
            location = Inventory.get_location_for_placing_item(item,
                (self.item_cell[0], self.item_cell[1]))
            self.mc.click_at_location(location)
            self.logger.info("Placed item back into the inventory")
            return StepStatus(False, Error.COULD_NOT_PLACE_ITEM_IN_STASH)

        return StepStatus(True)
