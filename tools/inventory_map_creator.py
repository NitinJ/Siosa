import json
import logging
import os
import sys
from functools import cmp_to_key

import pyautogui
from cv2 import cv2

from siosa.image.inventory_scanner import InventoryScanner
from siosa.location.in_game_location import InGameLocation
from siosa.location.location_factory import LocationFactory, Locations
from siosa.location.resolution import Resolution

FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
logging.basicConfig(format=FORMAT)


def crop_image(img, location):
    x1 = location.x1
    y1 = location.y1
    x2 = location.x2
    y2 = location.y2
    cropped_img = img[y1:y2, x1:x2]
    cv2.imshow('cropped_img', cropped_img)
    cv2.waitKey(0)
    return cropped_img


def sortkey(loc1: InGameLocation, loc2: InGameLocation):
    if loc1.y1 == loc2.y1:
        return loc1.x1 - loc2.x1
    return loc1.y1 - loc2.y1


def get_data(inventory_image=None):
    """
    Args:
        stash_type:
    """
    pyautogui.confirm(
        text='Press OK to grab inventory coordinates',
        title='Grab template',
        buttons=['OK'])

    scanner = InventoryScanner(debug=True, inventory_image=inventory_image)
    locations = sorted(scanner.get_empty_cell_locations(),
                       key=cmp_to_key(sortkey))
    cells_to_screen_location = {}

    print(locations)
    assert len(locations) == 60

    for r in range(0, 5):
        for c in range(0, 12):
            i = 12 * r + c
            key = '{},{}'.format(r, c)
            cells_to_screen_location[key] = locations[i].get_center()
            i += 1
    print("cells({}) : {}".format(len(cells_to_screen_location),
                                  cells_to_screen_location))
    return cells_to_screen_location


def get_file_path(location_factory):
    """
    Args:
        stash_type:
    """

    def parent(f): return os.path.dirname(os.path.abspath(f))

    path = os.path.join(parent(parent(__file__)), "siosa")
    path = os.path.join(path, "resources")
    path = os.path.join(path, "inventory")
    return os.path.join(path, "inventory_{}.json".format(location_factory.resolution))


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    resolution = None
    inventory_image = None
    lf = None

    if len(sys.argv) > 1:
        # See if we need to read the image from disk instead of taking a
        # screenshot.
        path = sys.argv[1]
        image = cv2.imread(path)
        h,w = image.shape[0:2]
        resolution = Resolution(w, h)
        lf = LocationFactory(resolution=resolution)
        inventory_image = crop_image(image, lf.get(Locations.INVENTORY))

    if not lf:
        lf = LocationFactory()

    if not lf.base_resolution.equals(lf.resolution):
        print("Resolution should be one of the base resolutions !")
        sys.exit(1)

    data = get_data(inventory_image)
    file_path = get_file_path(lf)
    with open(file_path, "w+") as outfile:
        json.dump(data, outfile)
    print("Created inventory map @ {}".format(file_path))
