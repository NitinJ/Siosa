import logging
import time

import cv2.cv2 as cv2
import numpy as np
import pyautogui

from siosa.control.window_controller import WindowController
from siosa.image.scikit_template_matcher import ScikitTemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.image.utils import grab_screenshot
from siosa.location.in_game_location import InGameLocation
from siosa.location.location_factory import LocationFactory, Locations


def _transform_points(points, res_from, res_to):
    f = (res_to.w / res_from.w, res_to.h / res_from.h)
    return [(int(p[0] * f[0]), int(p[1] * f[1])) for p in points]


class TemplateMatcher:
    def __init__(self, template, threshold=0.75, debug=False, scale=1.0):
        """
        Args:
            template:
            threshold:
            debug:
            scale:
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.wc = WindowController()
        self.stm = ScikitTemplateMatcher(debug=debug, threshold=threshold)
        self.debug = debug
        self.template = template
        self.image_cache = {}
        self.scale = scale

    def get_image_for_location(self, location: InGameLocation):
        return grab_screenshot(location)

    def get_image(self, location: InGameLocation, reuse):
        """
        Args:
            location:
            reuse:
        """
        # Params for the part of the screen to capture.
        key = str(location)
        if reuse and key in self.image_cache.keys():
            self.logger.info("Screen location image found in cache. Reusing.")
            return self.image_cache[key]

        image_rgb = self.get_image_for_location(location)
        width = location.get_width()
        height = location.get_height()

        # Resize image down to the resolution of the template and save the
        # processed image in cache.
        image_rgb = self._resize_image(
            np.array(image_rgb), location.resolution, width, height)

        self.image_cache[key] = self.template.process_image(image_rgb)
        return self.image_cache[key]

    def _resize_image(self, image_bytes, image_resolution, image_width,
                      image_height):
        """
        Resizes the given image to the resolution of the template and the scale
        factor.
        Args:
            image_bytes:
            image_resolution:
            image_width:
            image_height:

        Returns:

        """
        if self.template.resolution.equals(image_resolution):
            return image_bytes

        self.logger.debug(
            "Image resolution: {}x{}, "
            "template resolution: {}x{}".format(
                image_resolution.w,
                image_resolution.h,
                self.template.resolution.w,
                self.template.resolution.h))

        # Keep aspect ratio same.
        new_h = round(image_height * self.scale * (
                self.template.resolution.h / image_resolution.h))
        new_w = round(new_h * (image_width / image_height))

        if new_w != image_width or new_h != image_height:
            self.logger.debug("New image: w:{}, h:{}".format(new_w, new_h))

        return cv2.resize(image_bytes, (new_w, new_h),
                          interpolation=cv2.INTER_AREA)

    def _check_if_poe_is_in_foreground(self):
        if not self.wc.is_poe_in_foreground2():
            pyautogui.confirm(
                text='Move to POE and press OK',
                title='Grab image',
                buttons=['OK'])
            time.sleep(2)
        if not self.wc.is_poe_in_foreground2():
            self.logger.error("POE is not in foreground to capture "
                              "template.")
            raise (Exception("Path of Exile is not in foreground"))

    def clear_image_cache(self):
        self.image_cache = {}

    def match(self, location: InGameLocation, reuse=False):
        """Matches the template on a given screen location. :param location: The
        location of the screen to match template with. :param reuse: Whether to
        reuse an already taken image or not.

        Args:
            location:
            reuse:

        Returns:
            The positions (relative to the location) of matches with template.
        """
        if self.debug:
            self._check_if_poe_is_in_foreground()
        points = self.stm.match(self.get_image(location, reuse),
                                self.template.get(self.scale),
                                name=self.template.template_name)

        # Convert points back to the location resolution as these are with
        # respect to the template resolution.
        return _transform_points(
            points, self.template.resolution, location.resolution)

    def match_exists(self, location: InGameLocation, reuse=False):
        """Checks the template on a given screen location. :param location: The
        location of the screen to match template with. :param reuse: Whether to
        reuse an already taken image or not.

        Args:
            location:
            reuse:

        Returns: Whether the template exists at location or not.
        """
        if self.debug:
            self._check_if_poe_is_in_foreground()
        return self.stm.match_exists(self.get_image(location, reuse),
                                     self.template.get(self.scale),
                                     name=self.template.template_name)


if __name__ == "__main__":
    FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s - %(" \
             "funcName)s() ] %(message)s "
    logging.basicConfig(level=logging.INFO, format=FORMAT)
    tm = TemplateMatcher(
        TemplateRegistry.INVENTORY_0_0.get(),
        debug=True, threshold=0.75)
    print(tm.match(LocationFactory().get(Locations.INVENTORY)))
