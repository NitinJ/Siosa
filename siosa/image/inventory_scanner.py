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
        self.inventory = self.lf.get(Locations.INVENTORY)
        self.tm = TemplateMatcher(
            Template.from_registry(TemplateRegistry.INVENTORY_0_0), debug=debug)

    def scan(self):
        empty_cell_locations = self.tm.match(self.inventory)
        cells_with_items = \
            self.grid.get_cells_not_in_positions(empty_cell_locations)
        return sorted(cells_with_items, key=(lambda x: x[1]))
