import logging

import mss
import mss.tools

from siosa.clipboard.poe_clipboard import PoeClipboard
from siosa.control.game_step import Step
from siosa.control.steps.change_stash_tab_step import ChangeStashTab
from siosa.data.stash import Stash
from siosa.image.inventory_scanner import InventoryScanner
from siosa.location.location_factory import LocationFactory, Locations


class CleanInventory(Step):
    def __init__(self, game_state):
        Step.__init__(self, game_state)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self.clipboard = PoeClipboard()
        self.inventory_scanner = InventoryScanner()
        self.inventory_items = self.game_state.get()['inventory']
        self.stash_tab_index = self.game_state.get()['open_stash_tab_index']
        # Positions already moved to stash.
        self.moved_to_stash = []

    def execute(self):
        self.logger.info("Executing step: {}".format(__name__))

        if not self.game_state.get()['stash_open']:
            raise Exception("Stash is not open. Cannot move items")

        if not self.inventory_items:
            # Empty inventory.
            return

        item_positions_for_failed_moves = []
        item_positions = self.inventory_scanner.scan()

        while item_positions:
            self.logger.debug(
                "Got {} item_positions".format(len(item_positions)))

            items = self._get_items_in_positions(item_positions)
            item = self._get_next_item(items)
            self._move_item_to_stash(item)

            # Get item positions again.
            item_positions_new = self.inventory_scanner.scan()

            if not self._find_diff(item_positions, item_positions_new):
                # There is no diff between new inventory items and previous one,
                # means that we weren't able to move the item to current stash.
                # Move the item position to an array to move all these items to
                # dump stash later
                item_positions_for_failed_moves.append(item['position'])

            # Remove positions for items which failed to move.
            item_positions = self._find_diff(
                item_positions_new, item_positions_for_failed_moves)

        dump_stash_tabs = Stash().get_dump_stash_tabs()
        if not dump_stash_tabs:
            raise Exception("Cannot find any dump stash tabs !")

        failed_to_move_items = self._get_items_in_positions(
            item_positions_for_failed_moves)
        for item in failed_to_move_items:
            self._move_item_to_stash(item, stash_tab=dump_stash_tabs[0])

        if self.inventory_scanner.scan():
            # Somehow couldnt' move some items to stash.
            raise Exception("Couldn't move some/all items to stash. \
                 Probably dump stash tab is also full")

        self.game_state.update({'inventory': []})

    def _find_diff(self, list_a, list_b):
        """Returns A-B

        Args:
            list (arry): List A
            list_new (array): List B

        Returns:
            [type]: [description]
        """
        return list(set(list_a).difference(set(list_b)))

    def _get_next_item(self, items):
        """Returns the item to move to stash from a given list of items. Item 
        to be moved is selected based on current stash index and the stash 
        index to which an item belongs to.

        Args:
            items (array): List of items to select item from

        Returns:
            item: Item to move to stash.
        """
        item = self._get_item_for_stash_index(items, self.stash_tab_index)
        if not item:
            # We couldn't find an item for the current stash index. Need to move
            # on to the next available item and change stash index accordingly.
            self.logger.debug(
                "Couldn't find an item for stash index {}".format(
                    self.stash_tab_index))
            # Sort the item list by stash tab proximity to the current stash tab
            items.sort(key=(lambda item: abs(
                item['stash_tab'].index - self.stash_tab_index)))
            item = items[0]
        else:
            self.logger.debug(
                "Found an item({}) for stash index({})".format(
                    item['item'].type, self.stash_tab_index))
        return item

    def _get_item_for_stash_index(self, items, stash_index):
        """Returns an item from a list of items which belongs to the given
        stash index.

        Args:
            items (array): List of items
            stash_index (int): Stash index to return item for.

        Returns:
            Item: Item to move to given stash index.
        """
        for item in items:
            if item['stash_tab'].index == stash_index:
                return item
        return None

    def _move_item_to_stash(self, item, stash_tab=None):
        index = stash_tab.index if stash_tab else item['stash_tab'].index

        if index != self.stash_tab_index:
            self._change_stash_tab_index(index)

        self.logger.debug("Moving item({}:{}) to stash({})".format(
            item['item'].get_name(), item['item'].type, item['stash_tab'].index))

        self.mc.move_mouse(self._get_location(item['position'][0], item['position'][1]))
        self.kc.hold_modifier('Ctrl')
        self.mc.click()
        self.kc.unhold_modifier('Ctrl')
        self.moved_to_stash.append(item['position'])

    def _change_stash_tab_index(self, index):
        """Changes stash tab to a given index.

        Args:
            index (int): Index of the stash tab.
        """
        self.logger.debug("Current item's stash({}) is not equal to \
            current_stash({})".format(index, self.stash_tab_index))
        ChangeStashTab(self.game_state, index).execute()
        self.stash_tab_index = index

    def _get_items_in_positions(self, positions):
        """Returns items in the given positions.

        Args:
            positions (array): Positions for which to return items

        Returns:
            array: Items in given positions. These are proper item objects and 
            not inventory item objects.
        """
        items = []
        for inventory_item in self.inventory_items:
            if inventory_item['position'] in positions:
                items.append(inventory_item)
        return items

    def _get_location(self, r, c):
        # Invent box size
        size_x = Locations.INVENTORY_0_0.get_width() + 3
        size_y = Locations.INVENTORY_0_0.get_height() + 3

        # Location of (0, 0)
        x, y = Locations.INVENTORY_0_0.get_center()

        x2 = x + c * size_x
        y2 = y + r * size_y
        return LocationFactory().create(x2, y2, x2, y2)
