from siosa.clipboard.poe_clipboard import PoeClipboard
from siosa.control.mouse_controller import MouseController
from siosa.image.grid import Grid
from siosa.location.location_factory import LocationFactory, Locations


class Inventory:
    """
    Util methods for inventory related stuff.
    """

    BORDER = 2
    ROWS = 5
    COLUMNS = 12

    @staticmethod
    def is_in_bounds(p):
        """
        Returns whether a given cell is in inventory bounds
        Args:
            p: The cell to check for

        Returns: Whether the cell is in bounds.

        """
        # TODO: Use this method to validate input in other methods in
        # this class
        return p and 0 <= p[0] < Inventory.ROWS and 0 <= p[
            1] < Inventory.COLUMNS

    @staticmethod
    def get_location(p):
        """
        Returns the absolute position for a given inventory cell on the screen.
        Args:
            p: The cell

        Returns:
            Absolute position of the cell center on the screen.
        """
        lf = LocationFactory()
        inventory_0_0 = lf.get(Locations.INVENTORY_0_0)
        x, y = inventory_0_0.get_center()

        size_x = inventory_0_0.get_width() + Inventory.BORDER
        size_y = inventory_0_0.get_height() + Inventory.BORDER

        x2 = x + p[1] * size_x
        y2 = y + p[0] * size_y
        return lf.create(x2, y2, x2, y2)

    @staticmethod
    def get_location_for_placing_item(item, p):
        """
        Returns the InGameLocation on which an item needs to be placed so that
        item occupies the given cell in the inventory.
        Args:
            item: The item to place.
            p: The cell in which to place the item.
        Returns: The inGameLocation
        throws Exception if item doesn't have dimensions
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
        """
        Returns the item present in the given inventory cell.
        Args:
            p: The cell
            get_dimensions: Whether to get dimensions of the item as well. This
            is a costly operation.

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
        """
        Returns the dimensions of the item present in the given inventory cell.
        Args:
            item: Item
            p: The cell in which item is present.
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
