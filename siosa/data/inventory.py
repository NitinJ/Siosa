import json
import os

from siosa.clipboard.poe_clipboard import PoeClipboard
from siosa.common.util import parent
from siosa.control.mouse_controller import MouseController
from siosa.image.grid import Grid
from siosa.location.in_game_location import InGameLocation
from siosa.location.location import Location
from siosa.location.location_factory import LocationFactory, Locations
from siosa.location.resolution import Resolutions


class Inventory:
    """Util methods for inventory related stuff."""

    BORDER = 2
    ROWS = 5
    COLUMNS = 12

    _inventory_cell_location_map = {}

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
    def _get_path(filename):
        """
        Args:
            filename:
        """
        siosa_base = parent(parent(__file__))
        return os.path.join(siosa_base,
                            "resources/inventory/{}".format(filename))

    @staticmethod
    def _get_inventory_cell_location_map():
        if Inventory._inventory_cell_location_map:
            return Inventory._inventory_cell_location_map

        lf = LocationFactory()
        filename = 'inventory.json'
        filepath = Inventory._get_path(filename)
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
    def get_location(cell):
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
