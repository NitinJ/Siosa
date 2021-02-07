import logging

from siosa.image.grid import Grid
from siosa.image.template import Template
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import LocationFactory, Locations


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

    def is_empty(self, cell):
        self.logger.debug(
            "Checking if cell({}, {}) is empty".format(cell[0], cell[1]))
        points = self.tm.match(self.grid.get_cell_location(cell))
        if points:
            self.logger.debug(
                "Cell({}, {}) is empty".format(cell[0], cell[1]))
            return True
        return False

    def get_cell_location(self, cell):
        return self.grid.get_cell_location(cell)
