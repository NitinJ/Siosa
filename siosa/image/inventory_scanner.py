import logging
import os
from pprint import pprint

from cv2 import cv2

from siosa.common.util import parent
from siosa.config.siosa_config import SiosaConfig
from siosa.control.console_controller import ConsoleController
from siosa.control.mouse_controller import MouseController
from siosa.data.currency_exchange import CurrencyExchange
from siosa.data.inventory import Inventory
from siosa.data.stash import Stash
from siosa.image.utils import grayscale, invert, grab_screenshot
from siosa.location.location_factory import LocationFactory, Locations
from siosa.network.poe_api import PoeApi


def process_inventory_image(img):
    ret, threshold = cv2.threshold(img, 20, 255, cv2.THRESH_BINARY)
    image = grayscale(threshold)
    ret, image = cv2.threshold(image, 20, 255, cv2.THRESH_BINARY)
    image = invert(image)
    return image


class InventoryScanner:
    # We find all contours larger than inventory size. Also take a smaller
    # fraction as contour area might be slightly smaller
    INVENTORY_CELL_AREA = 2000

    def __init__(self, debug=False):
        """
        Args:
            debug:
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self.cc = ConsoleController()
        self.lf = LocationFactory()
        self.debug = debug

    def _get_empty_cells_using_contours(self):
        image_original = grab_screenshot(self.lf.get(Locations.INVENTORY))
        image = process_inventory_image(image_original)
        contours, hierarchy = cv2.findContours(
            image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        emtpy_cells = []
        for c in contours:
            if cv2.contourArea(c) > InventoryScanner.INVENTORY_CELL_AREA:
                x, y, w, h = cv2.boundingRect(c)
                center = (x + w // 2, y + h // 2)
                if self.debug:
                    image = cv2.rectangle(
                        image_original, center, center, (0, 255, 0), 6)
                emtpy_cells.append(center)

        if self.debug:
            cv2.imshow('Contours', image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return emtpy_cells

    def get_inventory(self, callback=None):
        """
        Returns: An inventory object representing the current inventory.
        """
        item_cells = {}
        cell_item_map = {}
        for p in self.scan():
            if p in item_cells:
                # The current position is part of an already scanned item, so
                # skip it.
                continue

            item = Inventory.get_item_at_cell(p)
            if not item:
                continue
            cell_item_map[p] = item

            # Mark the cells which this item occupies.
            InventoryScanner._mark_item_cells(p, item, item_cells)

            if callback:
                callback()
        return Inventory(cell_item_map)

    def scan(self):
        """
        Returns: The cells which contain items.
        """
        cells_with_items = {}
        for r in range(0, Inventory.ROWS):
            for c in range(0, Inventory.COLUMNS):
                cells_with_items[(r, c)] = 1

        empty_cell_locations = self._get_empty_cells_using_contours()
        for location in empty_cell_locations:
            # Locations are wrt. the matched area (Locations.INVENTORY)
            # We need to translate these to get on screen locations.
            base = self.lf.get(Locations.INVENTORY)
            location = (location[0] + base.x1, location[1] + base.y1)
            cell = Inventory.get_cell(location)
            if cell in cells_with_items:
                cells_with_items.pop(cell)
        return sorted(cells_with_items, key=(lambda x: x[1]))

    @staticmethod
    def _mark_item_cells(p, item, cells):
        """
        Args:
            p:
            item:
            cells:
        """
        w, h = item.get_dimensions()
        if not w or not h:
            w = 1
            h = 1
        p2 = (p[0] + h - 1, p[1] + w - 1)
        for i in range(p[0], p2[0] + 1):
            for j in range(p[1], p2[1] + 1):
                cells[(i, j)] = True


if __name__ == "__main__":
    FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s - %(" \
             "funcName)s() ] %(message)s "
    logging.basicConfig(level=logging.INFO, format=FORMAT)

    lf = LocationFactory()
    exchange = CurrencyExchange(
        PoeApi("MopedDriverr", "0dfdc62a6d647095161d19e802961ef3",
               "Expedition"))
    config_file_path = os.path.join(parent(parent(parent(__file__))),
                                    "config.json")
    config = SiosaConfig.create_from_file(config_file_path)
    stash = Stash(config)

    scanner = InventoryScanner(debug=False)
    mc = MouseController(LocationFactory())
    cells = scanner.scan()
    print(cells)

    iv = scanner.get_inventory()
    pprint(iv.grid)
    print(iv.item_positions)
