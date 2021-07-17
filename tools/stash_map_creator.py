import json
import logging
import os

import pyautogui

from siosa.image.grid import Grid
from siosa.image.template import Template
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import LocationFactory, Locations

FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
logging.basicConfig(format=FORMAT)

lf = LocationFactory()


def get_template(stash_type):
    """
    Args:
        stash_type:
    """
    if stash_type == 'normal':
        return Template.from_registry(TemplateRegistry.NORMAL_STASH_0_0)
    return Template.from_registry(TemplateRegistry.QUAD_STASH_0_0)


def get_grid(stash_type):
    """
    Args:
        stash_type:
    """
    if stash_type == 'normal':
        return Grid(Locations.STASH_TAB, Locations.STASH_NORMAL_0_0, 12, 12, 2,
                    2)
    return Grid(Locations.STASH_TAB, Locations.STASH_QUAD_0_0, 24, 24, 2, 2)


def get_data(stash_type):
    """
    Args:
        stash_type:
    """
    if stash_type not in ('quad', 'normal'):
        return

    grid = get_grid(stash_type)
    template = get_template(stash_type)
    match_location = LocationFactory().get(Locations.STASH_TAB)

    pyautogui.confirm(
        text='Press OK to verify template({}) on location({})'.format(
            template,
            match_location.name),
        title='Grab template',
        buttons=['OK'])
    tm = TemplateMatcher(template, debug=True, confirm_foreground=False)

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


def get_file_path(stash_type):
    """
    Args:
        stash_type:
    """
    def parent(f): return os.path.dirname(os.path.abspath(f))

    path = os.path.join(parent(parent(__file__)), "siosa")
    path = os.path.join(path, "resources")
    path = os.path.join(path, "stash")
    return os.path.join(path, stash_type + ".json")


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    stash_type = 'normal'
    data = get_data(stash_type)

    file_path = get_file_path(stash_type)
    with open(file_path, "w+") as outfile:
        json.dump(data, outfile)
