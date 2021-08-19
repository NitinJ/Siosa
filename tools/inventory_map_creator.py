import json
import logging
import os

import pyautogui

from siosa.data.inventory import Inventory
from siosa.image.grid import Grid
from siosa.image.template import Template
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import LocationFactory, Locations

FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
logging.basicConfig(format=FORMAT)

lf = LocationFactory()


def get_data():
    """
    Args:
        stash_type:
    """
    grid = Grid(
        Locations.INVENTORY,
        Locations.INVENTORY_0_0,
        Inventory.ROWS,
        Inventory.COLUMNS,
        Inventory.BORDER,
        Inventory.BORDER)
    template = TemplateRegistry.INVENTORY_0_0.get()
    match_location = LocationFactory().get(Locations.INVENTORY)

    pyautogui.confirm(
        text='Press OK to verify template({}) on location({})'.format(
            template,
            match_location),
        title='Grab template',
        buttons=['OK'])
    tm = TemplateMatcher(template, debug=True)

    # Points are relative to the match location.
    points = tm.match(match_location)
    logger.debug("Points for all stash cells: {}".format(points))

    cells_to_screen_location = {}
    for point in points:
        cell = grid.get_cells_in_positions([point])[0]
        if cell in cells_to_screen_location.keys():
            continue
        point_screen_full = [
            int(point[0] + match_location.x1),
            int(point[1] + match_location.y1)]
        key = ','.join([str(i) for i in cell])
        cells_to_screen_location[key] = point_screen_full
    print("cells({}) : {}".format(len(cells_to_screen_location),
                                  cells_to_screen_location))
    return cells_to_screen_location


def get_file_path():
    """
    Args:
        stash_type:
    """
    def parent(f): return os.path.dirname(os.path.abspath(f))

    path = os.path.join(parent(parent(__file__)), "siosa")
    path = os.path.join(path, "resources")
    path = os.path.join(path, "inventory")
    return os.path.join(path, "inventory.json")


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    data = get_data()

    file_path = get_file_path()
    with open(file_path, "w+") as outfile:
        json.dump(data, outfile)
