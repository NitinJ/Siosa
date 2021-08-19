import logging

from siosa.control.console_controller import ConsoleController
from siosa.data.inventory import Inventory
from siosa.image.grid import Grid
from siosa.image.template import Template
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import LocationFactory, Locations


class InventoryScanner:
    def __init__(self, debug=False):
        """
        Args:
            debug:
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self.cc = ConsoleController()
        self.lf = LocationFactory()
        self.grid = Grid(
            Locations.INVENTORY,
            Locations.INVENTORY_0_0,
            Inventory.ROWS,
            Inventory.COLUMNS,
            Inventory.BORDER,
            Inventory.BORDER)
        self.tm = TemplateMatcher(TemplateRegistry.INVENTORY_0_0.get(),
                                  debug=False, threshold=0.75)

    def scan(self):
        cells_with_items = {}
        for r in range(0, Inventory.ROWS):
            for c in range(0, Inventory.COLUMNS):
                cells_with_items[(r, c)] = 1

        empty_cell_locations = self.tm.match(self.lf.get(Locations.INVENTORY))
        for location in empty_cell_locations:
            # Locations are wrt. the matched area (Locations.INVENTORY)
            # We need to translate these to get on screen locations.
            base = self.lf.get(Locations.INVENTORY)
            location = (location[0] + base.x1, location[1] + base.y1)
            cell = Inventory.get_cell(location)
            if cell in cells_with_items:
                cells_with_items.pop(cell)
        return sorted(cells_with_items, key=(lambda x: x[1]))


if __name__ == "__main__":
    FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s - %(" \
             "funcName)s() ] %(message)s "
    logging.basicConfig(level=logging.INFO, format=FORMAT)
    iscanner = InventoryScanner()
    print(iscanner.scan())
