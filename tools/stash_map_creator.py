import json
import logging
import os
import sys
from functools import cmp_to_key

import pyautogui
from cv2 import cv2

from siosa.image.grid import Grid
from siosa.image.stash_tab_scanner import StashTabScanner
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import LocationFactory, Locations
from siosa.location.resolution import Resolution

FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
logging.basicConfig(format=FORMAT)


def get_template(stash_type):
    """
    Args:
        stash_type:
    """
    if stash_type == 'normal':
        return TemplateRegistry.NORMAL_STASH_0_0.get()
    return TemplateRegistry.QUAD_STASH_0_0.get()


def get_grid(stash_type):
    """
    Args:
        stash_type:
    """
    if stash_type == 'normal':
        return Grid(Locations.STASH_TAB, Locations.STASH_NORMAL_0_0, 12, 12, 2,
                    2)
    return Grid(Locations.STASH_TAB, Locations.STASH_QUAD_0_0, 24, 24, 2, 2)


class StashTabFake:
    def __init__(self, is_quad, size, cell_border):
        self.is_quad = is_quad
        self.size = size
        self.cell_border_x = cell_border[0]
        self.cell_border_y = cell_border[1]


def get_data(stash_type, lf, stash_image=None):
    """
    Args:
        stash_type:
    """
    grid = get_grid(stash_type)
    match_location = LocationFactory().get(Locations.STASH_TAB)
    pyautogui.confirm(
        text='Press OK to grab {} stash coordinates'.format(stash_type),
        title='Grab template',
        buttons=['OK'])

    size = (12, 12) if stash_type == 'normal' else (24, 24)
    tab = StashTabFake(stash_type == 'quad', size, (1, 1))
    scanner = StashTabScanner(tab, stash_image=stash_image, debug=True)
    locations = sorted(scanner.get_empty_cell_locations(),
                       key=cmp_to_key(sortkey))
    in_game_locations = []
    base = lf.get(Locations.STASH_TAB)
    for location in locations:
        # Convert locations to in game locations
        location = (location[0] + base.x1, location[1] + base.y1)
        in_game_locations.append(
            lf.create(
                location[0], location[1], location[0], location[1]))

    cells_to_screen_location = {}
    print(in_game_locations)
    assert len(in_game_locations) == (size[0] * size[1]), len(in_game_locations)

    for r in range(0, size[0]):
        for c in range(0, size[1]):
            i = size[0] * r + c
            key = '{},{}'.format(r, c)
            cells_to_screen_location[key] = in_game_locations[i].get_center()
            i += 1
    print("cells({}) : {}".format(len(cells_to_screen_location),
                                  cells_to_screen_location))
    return cells_to_screen_location


def get_file_path(stash_type, location_factory):
    """
    Args:
        stash_type:
    """
    def parent(f): return os.path.dirname(os.path.abspath(f))

    path = os.path.join(parent(parent(__file__)), "siosa")
    path = os.path.join(path, "resources")
    path = os.path.join(path, "stash")
    return os.path.join(path, stash_type + "{}.json".format(
        location_factory.resolution))

def crop_image(img, location):
    x1 = location.x1
    y1 = location.y1
    x2 = location.x2
    y2 = location.y2
    cropped_img = img[y1:y2, x1:x2]
    cv2.imshow('cropped_img', cropped_img)
    cv2.waitKey(0)
    return cropped_img


def sortkey(loc1, loc2):
    if loc1[1] == loc2[1]:
        return loc1[0] - loc2[0]
    return loc1[1] - loc2[1]


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    if len(sys.argv) < 2:
        print("Stash tab type(normal/quad) not provided")
        sys.exit(1)

    resolution = None
    stash_image = None
    lf = None
    stash_type = sys.argv[1]

    if stash_type not in ('quad', 'normal'):
        print("Invalid stash type")
        sys.exit(1)

    if len(sys.argv) > 2:
        # See if we need to read the image from disk instead of taking a
        # screenshot.
        path = sys.argv[2]
        image = cv2.imread(path)
        h,w = image.shape[0:2]
        resolution = Resolution(w, h)
        lf = LocationFactory(resolution=resolution)
        stash_image = crop_image(image, lf.get(Locations.STASH_TAB))

    if not lf:
        lf = LocationFactory()
    if not lf.base_resolution.equals(lf.resolution):
        print("Resolution should be one of the base resolutions !")
        sys.exit(1)

    data = get_data(stash_type, lf, stash_image=stash_image)
    file_path = get_file_path(stash_type, lf)
    with open(file_path, "w+") as outfile:
        json.dump(data, outfile)
    print("Created stash map @ {}".format(file_path))