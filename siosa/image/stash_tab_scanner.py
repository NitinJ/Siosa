import logging

from cv2 import cv2

from siosa.data.stash_cell_locations import StashCellLocation
from siosa.image.grid import Grid
from siosa.image.utils import grab_screenshot, grayscale, invert
from siosa.location.location import Location
from siosa.location.location_factory import LocationFactory, Locations


def process_inventory_image(img):
    ret, threshold = cv2.threshold(img, 20, 255, cv2.THRESH_BINARY)
    image = grayscale(threshold)
    ret, image = cv2.threshold(image, 20, 255, cv2.THRESH_BINARY)
    image = invert(image)
    return image


class StashTabScanner:
    """Only supports normal and quad stash tabs. Requires that the stash tab is
    open in game.
    """

    def __init__(self, stash_tab, debug=False):
        """
        Args:
            stash_tab:
            debug:
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.lf = LocationFactory()
        self.stash_tab = stash_tab
        self.cell_0_0 = Locations.STASH_QUAD_0_0 if self.stash_tab.is_quad \
            else Locations.STASH_NORMAL_0_0
        self.min_contour_area = 500 if self.stash_tab.is_quad else 2000
        self.debug = debug
        self.grid = Grid(
            Locations.STASH_TAB,
            self.cell_0_0,
            self.stash_tab.size[0],
            self.stash_tab.size[1],
            self.stash_tab.cell_border_x,
            self.stash_tab.cell_border_y)

    def _get_empty_cells_using_contours(self):
        image_original = grab_screenshot(self.lf.get(Locations.STASH_TAB))
        image = process_inventory_image(image_original)
        contours, hierarchy = cv2.findContours(
            image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        emtpy_cells = []
        for c in contours:
            if cv2.contourArea(c) > self.min_contour_area:
                x, y, w, h = cv2.boundingRect(c)
                center = (x + w // 2, y + h // 2)
                if self.debug:
                    image = cv2.rectangle(
                        image_original, center, center, (0, 0, 255), 4)
                emtpy_cells.append(center)

        if self.debug:
            cv2.imshow('Contours', image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return emtpy_cells

    def get_item_cells(self):
        """Returns: Cells at which items are present."""
        return self.grid.get_cells_not_in_positions(
            self._get_empty_cells_using_contours())

    def is_empty(self, cell):
        """
        Args:
            cell:
        """
        self.logger.debug(
            "Checking if cell ({}, {}) is empty".format(cell[0], cell[1]))
        empty_cells = self.grid.get_cells_in_positions(
            self._get_empty_cells_using_contours())
        if cell in empty_cells:
            self.logger.debug("Cell({}, {}) is empty".format(cell[0], cell[1]))
            return True
        return False

    def get_cell_location(self, cell):
        """
        Args:
            cell:
        """
        return StashCellLocation.get_cell_location(self.stash_tab.is_quad, cell)

    def get_location_for_placing_item(self, cell, item_dimensions):
        """Returns the location on which a given item needs to be placed if item
        needs to be in the given cell. For example - A 4x2 item placed at (2, 2)
        will need to be placed at mid point of (2, 2) and (5, 3) :param cell:
        The cell location for the item (the top left cell) :param
        item_dimensions: The item

        Returns: The in game location for placing the item.

        Args:
            cell:
            item_dimensions:
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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="[%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s")

    class StashTabFake:
        def __init__(self, is_quad, size, cell_border):
            self.is_quad = is_quad
            self.size = size
            self.cell_border_x = cell_border[0]
            self.cell_border_y = cell_border[1]

    s = StashTabFake(True, (24, 24), (1, 1))
    scanner = StashTabScanner(s, debug=True)
    scanner.get_item_cells()
    print(scanner.is_empty((5, 5)))
