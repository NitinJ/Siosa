import time
from enum import Enum

from siosa.data.poe_item_factory import PoeItemFactory
from siosa.image.stash_tab_scanner import StashTabScanner
from siosa.network.poe_api import PoeApi


class StashTabType(Enum):
    UNKNOWN = 'Unknown'
    CURRENCY = 'CurrencyStash'
    MAP = 'MapStash'
    ESSENCE = 'EssenceStash'
    DIVINATION = 'DivinationCardStash'
    FRAGMENT = 'FragmentStash'
    UNIQUE = 'UniqueStash'
    METAMORPH = 'MetamorphStash'
    BLIGHT = 'BlightStash'
    DELVE = 'DelveStash'
    DELIRIUM = 'DeliriumStash'


class StashTab:
    REFRESH_DURATION = 5 * 60  # 5 minutes
    NORMAL_STASH_TAB_SIZE = (12, 12)
    QUAD_STASH_TAB_SIZE = (24, 24)
    NORMAL_STASH_TAB_BORDER_RIGHT = 2
    NORMAL_STASH_TAB_BORDER_BOTTOM = 2
    QUAD_STASH_TAB_BORDER_RIGHT = 1
    QUAD_STASH_TAB_BORDER_BOTTOM = 1

    def __init__(self, data):
        """
        Args:
            data:
        """
        self.api = PoeApi()
        self.type = data['type']
        self.index = int(data['index'])
        self.name = data['name']
        self.is_quad = bool(data['is_quad'])
        self.is_premium = bool(data['is_premium'])
        self.item_factory = PoeItemFactory()
        self.last_fetched_ts = 0

        # Only valid for normal and quad stash tabs.
        self.size = StashTab.QUAD_STASH_TAB_SIZE \
            if self.is_quad else StashTab.NORMAL_STASH_TAB_SIZE
        self.cell_border_x = StashTab.QUAD_STASH_TAB_BORDER_RIGHT \
            if self.is_quad else StashTab.NORMAL_STASH_TAB_BORDER_RIGHT
        self.cell_border_y = StashTab.QUAD_STASH_TAB_BORDER_BOTTOM \
            if self.is_quad else StashTab.NORMAL_STASH_TAB_BORDER_BOTTOM

        self.scanner = StashTabScanner(self)
        self.contents = []
        self.items = {}

    def get_type(self):
        for t in StashTabType:
            if t.value == self.type:
                return t
        return StashTabType.UNKNOWN

    def get_item_at_location(self, x, y):
        """Returns the item at given x,y co-ordinates in the stash tab. :param
        x: 0 indexed x co-ordinate :param y: 0 indexed y co-ordinate

        Args:
            x:
            y:
        """
        item = self._get_item(x, y)
        if item:
            return item
        items = self._get_contents()
        for item in items:
            if item['x'] == x and item['y'] == y:
                self.items[(x, y)] = self.item_factory.get_item(
                    item, source='stash')
                return self.items[(x, y)]
        return None

    def get_item_cells_ingame(self):
        """Returns: Returns the cells where items are present using in game
        data
        """
        return self.scanner.get_item_cells()

    def is_item_at_location_ingame(self, p):
        """Returns whether there is an item at x,y stash positions in this
        stash. :param p: cell

        Args:
            p:

        Returns:
            Whether there is an item present at x,y
        """
        return not self.scanner.is_empty((p[0], p[1]))

    def get_cell_location(self, cell):
        """Returns the in game location for a given stash cell.

        Args:
            cell:
        """
        return self.scanner.get_cell_location(cell)

    def get_cell_location_for_placing_item(self, cell, item_dimensions):
        """Returns the in game location for a given stash cell if an item needs
        to be placed in it. This location always is the center of lower right
        quadrant of the cell. This ensures that we always place the item
        correctly in the cell. Only works for normal and quad stash tabs.

        cell: The top left cell to place the item in. item_dimensions: The
        width, height tuple of item dimensions.

        Args:
            cell:
            item_dimensions:
        """
        assert (self.is_quad or self.is_premium)
        return self.scanner.get_location_for_placing_item(cell, item_dimensions)

    def _get_contents(self):
        if time.time() - self.last_fetched_ts > StashTab.REFRESH_DURATION:
            self._refresh_data()
        return self.contents

    def _refresh_data(self):
        self.contents = self.api.get_stash_contents(self.index)
        self.items = {}
        self.last_fetched_ts = time.time()

    def _get_item(self, x, y):
        """
        Args:
            x:
            y:
        """
        if (x, y) in self.items.keys():
            return self.items[(x, y)]
        return None

    def _is_in_bounds(self, position):
        """
        Args:
            position:
        """
        x = position[0]
        y = position[1]
        return (x >= 0 and y >= 0) and (x < self.size[0] and y < self.size[1])

    def __str__(self):
        return "type: {}, index: {}, name: {}, quad: {}, premium: {}".format(
            self.type,
            self.index,
            self.name,
            self.is_quad,
            self.is_premium)
