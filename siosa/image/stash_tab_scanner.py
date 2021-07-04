import logging

from siosa.image.grid import Grid
from siosa.image.template import Template
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location import Location
from siosa.location.location_factory import LocationFactory, Locations
from siosa.resources.stash.stash_cell_locations import StashCellLocation


class StashTabScanner:
    """
    Only supports normal and quad stash tabs. Requires that the stash tab is
    open in game.
    """

    def __init__(self, stash_tab, debug=False):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.lf = LocationFactory()
        self.stash_tab = stash_tab
        self.cell_0_0 = Locations.STASH_QUAD_0_0 if self.stash_tab.is_quad \
            else Locations.STASH_NORMAL_0_0
        self.grid = Grid(
            Locations.STASH_TAB,
            self.cell_0_0,
            self.stash_tab.size[0],
            self.stash_tab.size[1],
            self.stash_tab.cell_border_x,
            self.stash_tab.cell_border_y)

        registry = TemplateRegistry.QUAD_STASH_0_0 if \
            self.stash_tab.is_quad else TemplateRegistry.NORMAL_STASH_0_0
        self.tm = TemplateMatcher(Template.from_registry(registry), debug=debug)

    def get_item_cells(self):
        """
        Returns: Cells at which items are present.
        """
        return self.grid.get_cells_not_in_positions(
                self.tm.match(self.lf.get(Locations.STASH_TAB)))

    def is_empty(self, cell):
        self.logger.debug(
            "Checking if cell ({}, {}) is empty".format(cell[0], cell[1]))
        empty_cells = \
            self.grid.get_cells_in_positions(
                self.tm.match(self.lf.get(Locations.STASH_TAB)))
        if cell in empty_cells:
            self.logger.debug(
                "Cell({}, {}) is empty".format(cell[0], cell[1]))
            return True
        return False

    def get_cell_location(self, cell):
        return StashCellLocation.get_cell_location(self.stash_tab.is_quad, cell)

    def get_location_for_placing_item(self, cell, item_dimensions):
        """
        Returns the location on which a given item needs to be placed if item
        needs to be in the given cell. For example - A 4x2 item placed at (2, 2)
        will need to be placed at mid point of (2, 2) and (5, 3)
        Args:
            cell: The cell location for the item (the top left cell)
            item_dimensions: The item

        Returns: The in game location for placing the item.
        """
        w, h = item_dimensions
        cell_bot_right = (cell[0] + h - 1, cell[1] + w - 1)
        cell_top_left_x, cell_top_left_y = self.get_cell_location(
            cell).get_center()
        cell_bot_right, cell_bot_right_y = self.get_cell_location(
            cell_bot_right).get_center()
        midx, midy = (cell_top_left_x + cell_bot_right) // 2, (
                cell_top_left_y + cell_bot_right_y) // 2
        return self.lf.get(Location(midx, midy, midx, midy, self.lf.resolution))
