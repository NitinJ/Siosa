import json
import os

from siosa.clipboard.poe_clipboard import PoeClipboard
from siosa.common.util import parent
from siosa.control.mouse_controller import MouseController
from siosa.data.poe_item import Item
from siosa.image.grid import Grid
from siosa.location.in_game_location import InGameLocation
from siosa.location.location import Location
from siosa.location.location_factory import LocationFactory, Locations
from siosa.location.resolution import Resolutions


def _get_item_dimensions(item):
    w, h = item.get_dimensions()
    if not w:
        w = 2
    if not h:
        h = 3
    return w, h


def _update_item_stack_size(item, size):
    assert size <= item.item_info['max_stack_size']
    item.item_info['stack_size'] = size


def _get_path(filename):
    """
    Args:
        filename:
    """
    siosa_base = parent(parent(__file__))
    return os.path.join(siosa_base,
                        "resources/inventory/{}".format(filename))


class Inventory:
    """Util methods for inventory related stuff."""

    BORDER = 2
    ROWS = 5
    COLUMNS = 12

    _inventory_cell_location_map = {}

    def __init__(self, item_cell_map=None):
        if item_cell_map is None:
            item_cell_map = {}
        self.items = list(item_cell_map.values())

        self.item_positions = {}
        self.grid = [[0 for i in range(Inventory.COLUMNS)]
                     for j in range(Inventory.ROWS)]
        for position, item in item_cell_map.items():
            self.item_positions[position] = 1
            self._mark_occupied(position, item)

    def add_item(self, item: Item):
        if not item:
            return False

        item, updates = self._add_item_to_stacks(item)
        if not item:
            # Item can be completely added inventory item stacks. Apply updates.
            for update in updates:
                _update_item_stack_size(update[0], update[1])
            return True

        cell = self._find_cell_for_item(item)
        if not cell:
            # Couldn't find a cell to put item into.
            return False

        # Found a cell for item. Apply updates.
        for update in updates:
            _update_item_stack_size(update[0], update[1])

        self.item_positions[cell] = 1
        self._mark_occupied(cell, item)
        self.items.append(item)
        return True

    def _mark_occupied(self, cell, item):
        w, h = _get_item_dimensions(item)
        cell_to = (cell[0] + h - 1, cell[1] + w - 1)
        for r in range(cell[0], cell_to[0] + 1):
            for c in range(cell[1], cell_to[1] + 1):
                self.grid[r][c] = 1

    def _find_cell_for_item(self, item):
        w, h = _get_item_dimensions(item)
        for c in range(0, Inventory.COLUMNS):
            for r in range(0, Inventory.ROWS):
                cell = (r, c)
                cell_to = (r + h - 1, c + w - 1)
                if self._is_empty_and_in_bounds(cell, cell_to):
                    return cell
        return None

    def _is_empty_and_in_bounds(self, c1, c2):
        for r in range(c1[0], c2[0] + 1):
            for c in range(c1[1], c2[1] + 1):
                if not Inventory.is_in_bounds((r, c)):
                    return False
                if self.grid[r][c]:
                    return False
        return True

    def _add_item_to_stacks(self, item):
        """
        Adds an item to the inventory keeping track of item stacking.
        Args:
            item:

        Returns: Returns the final item to be added to the inventory and updates
        to existing item stacks. Doesn't apply updates. Updates are tuples of
        item: new_stack_size

        """
        updates = []
        if not item.is_stackable():
            return item, updates

        stack_size = item.get_stack_size()

        # Find item stacks in inventory which can fit this item and put stacks
        # into those inventory items.
        for inv_item in self.items:
            if inv_item.is_same_kind(item) and inv_item.is_stackable():
                inv_item_stack_size = inv_item.get_stack_size()
                inv_item_max_stack_size = inv_item.get_max_stack_size()

                if inv_item_stack_size == inv_item_max_stack_size:
                    continue

                stack_size_to_be_added = \
                    min(inv_item_max_stack_size - inv_item_stack_size,
                        stack_size)

                # Update inventory item stack size.
                updates.append((
                    inv_item, inv_item_stack_size + stack_size_to_be_added))

                stack_size = stack_size - stack_size_to_be_added
                if stack_size == 0:
                    # Item completely added to inv item stacks.
                    return None, updates

        assert stack_size > 0
        updates.append((item, stack_size))
        return item, updates

    @staticmethod
    def is_in_bounds(p):
        """Returns whether a given cell is in inventory bounds :param p: The
        cell to check for

        Returns: Whether the cell is in bounds.

        Args:
            p:
        """
        # TODO: Use this method to validate input in other methods in
        # this class
        return p and 0 <= p[0] < Inventory.ROWS and 0 <= p[
            1] < Inventory.COLUMNS

    @staticmethod
    def _get_inventory_cell_location_map():
        if Inventory._inventory_cell_location_map:
            return Inventory._inventory_cell_location_map

        lf = LocationFactory()
        filename = 'inventory.json'
        filepath = _get_path(filename)
        data = json.load(open(filepath, 'r'))
        ret = {}
        for key, location in data.items():
            cell = tuple(int(i) for i in key.split(","))
            # TODO: Take resolution as input from the file itself.
            location = Location(location[0],
                                location[1],
                                location[0],
                                location[1],
                                Resolutions.p1080)
            ret[cell] = lf.get(location)
        Inventory._inventory_cell_location_map = ret
        return Inventory._inventory_cell_location_map

    @staticmethod
    def get_location(cell) -> InGameLocation:
        """Returns the absolute position for a given inventory cell on the
        screen. :param cell: The cell

        Args:
            cell:

        Returns:
            Absolute position of the cell center on the screen.
        """
        cell = tuple(cell)
        return Inventory._get_inventory_cell_location_map()[cell]

    @staticmethod
    def get_cell(location):
        if not isinstance(location, InGameLocation):
            location = LocationFactory().create(
                location[0], location[1], location[0], location[1])

        cell_location_map = Inventory._get_inventory_cell_location_map()
        def distance(item):
            loc = item[1]
            loc_center = loc.get_center()
            location_center = location.get_center()
            return (loc_center[0] - location_center[0]) ** 2 + \
                   (loc_center[1] - location_center[1]) ** 2

        # Sort the cell locations wrt. distance from location and return the
        # cell.
        return sorted(cell_location_map.items(), key=distance)[0][0]

    @staticmethod
    def get_location_for_placing_item(item, p):
        """Returns the InGameLocation on which an item needs to be placed so
        that item occupies the given cell in the inventory. :param item: The
        item to place. :param p: The cell in which to place the item.

        Returns: The inGameLocation throws Exception if item doesn't have
        dimensions

        Args:
            item:
            p:
        """
        w, h = item.get_dimensions()
        if not w or not h:
            raise Exception("Item has no dimensions !")

        grid = Grid(
            Locations.INVENTORY,
            Locations.INVENTORY_0_0,
            Inventory.ROWS,
            Inventory.COLUMNS,
            Inventory.BORDER,
            Inventory.BORDER)
        cell_bottom_right = p[0] + h - 1, p[1] + w - 1
        location_top_left = grid.get_cell_location(p).get_center()
        location_bottom_right = grid.get_cell_location(
            cell_bottom_right).get_center()
        midx = (location_top_left[0] + location_bottom_right[0]) // 2
        midy = (location_top_left[1] + location_bottom_right[1]) // 2
        return LocationFactory().create(midx, midy, midx, midy)

    @staticmethod
    def get_item_at_cell(p, get_dimensions=False):
        """Returns the item present in the given inventory cell. :param p: The
        cell :param get_dimensions: Whether to get dimensions of the item as
        well. This :param is a costly operation.:

        Args:
            p:
            get_dimensions:

        Returns:
            The item present in the cell. Returns None if not present.
        """
        mc = MouseController()
        mc.move_mouse(Inventory.get_location(p))
        item = PoeClipboard().read_item_at_cursor()
        if get_dimensions:
            w, h = Inventory.get_item_dimensions(item, p)
            item.set_dimensions(w, h)
        return item

    @staticmethod
    def get_item_dimensions(item, p):
        """Returns the dimensions of the item present in the given inventory
        cell. :param item: Item :param p: The cell in which item is present.

        Args:
            item:
            p:

        Returns:
            The item dimensions tuple
        """
        key = str(item)
        mc = MouseController()
        w = 1
        h = 1

        # Get height
        i = p[0] + 1
        while i < Inventory.ROWS:
            cell = (i, p[1])
            mc.move_mouse(Inventory.get_location(cell))
            item = PoeClipboard().read_item_at_cursor()
            if item and str(item) == key:
                h += 1
            else:
                break
            i += 1

        # Get width
        i = p[1] + 1
        while i < Inventory.COLUMNS:
            cell = (p[0], i)
            mc.move_mouse(Inventory.get_location(cell))
            item = PoeClipboard().read_item_at_cursor()
            if item and str(item) == key:
                w += 1
            else:
                break
            i += 1
        return w, h
