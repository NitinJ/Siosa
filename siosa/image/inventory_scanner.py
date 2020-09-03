import logging

from siosa.control.console_controller import ConsoleController
from siosa.image.template_matcher import TemplateMatcher
from siosa.location.location_factory import LocationFactory, Locations


class InventoryScanner:
    ROWS = 5
    COLUMNS = 12

    def __init__(self, debug=False):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self.cc = ConsoleController()
        self.lf = LocationFactory()

        self.inventory = self.lf.get(Locations.INVENTORY)
        self.inventory_0_0 = self.lf.get(Locations.INVENTORY_0_0)

        self.tm = TemplateMatcher(self.inventory_0_0, debug=debug)

    def _clear_screen(self):
        self.cc.clear_console()

    def scan(self):
        points = self.tm.match(self.inventory)
        return self._convert_points_to_inventory_positions(points)

    def _convert_points_to_inventory_positions(self, points):
        center00_x, center00_y = self.inventory_0_0.get_center()
        offset_x, offset_y = (
            center00_x - self.inventory.x1,
            center00_y - self.inventory.y1)
        width = self.inventory_0_0.get_width()
        height = self.inventory_0_0.get_height()

        empty_positions = [
            (abs(p[1] - offset_y) // height, abs(p[0] - offset_x) // width)
            for p in points]
        item_positions = {}
        for i in range(0, InventoryScanner.ROWS):
            for j in range(0, InventoryScanner.COLUMNS):
                if (i, j) not in empty_positions:
                    item_positions[(i, j)] = 1
        self.logger.debug(
            "Found {} items at inventory cell locations: {}".format(
                len(item_positions), str(item_positions)))
        # Return column sorted.
        return sorted(item_positions, key=(lambda x: x[1]))
