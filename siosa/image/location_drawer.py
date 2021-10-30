import logging
import os

import cv2.cv2 as cv2
import mss
import mss.tools
import numpy as np
from PIL import Image
from siosa.location.location_factory import LocationFactory, Locations
from siosa.location.resolution import Resolution

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class LocationDrawer:
    @staticmethod
    def get_image(image_path):
        if not image_path or not os.path.exists(image_path):
            logger.debug("Reading image from screen.")
            return LocationDrawer.get_image_from_screen()
        return cv2.imread(image_path)

    @staticmethod
    def get_image_from_screen():
        lf = LocationFactory()
        full_screen_grab_params = LocationDrawer._get_grab_params(
            lf.get(Locations.SCREEN_FULL))
        with mss.mss() as sct:
            image = sct.grab(full_screen_grab_params)

        image_bytes_rgb = Image.frombytes(
            'RGB',
            (lf.resolution.w, lf.resolution.h),
            image.rgb)

        return cv2.cvtColor(np.array(image_bytes_rgb), cv2.COLOR_RGB2BGR)

    @staticmethod
    def get_location_factory(image_path):
        if not image_path:
            return LocationFactory()
        image = cv2.imread(image_path)
        h,w = image.shape[0:2]
        return LocationFactory(resolution=Resolution(w, h))

    @staticmethod
    def draw(location, image_path=None):
        """Draws the given location on screen :param location: The location of
        the screen to draw a rectangle on.

        Args:
            location:
        """
        image = LocationDrawer.get_image(image_path)
        lf = LocationDrawer.get_location_factory(image_path)
        location = lf.get(location)

        # Draw rectangle around image
        cv2.rectangle(image, (location.x1, location.y1),
                      (location.x2, location.y2),
                      (0, 255, 102), 4)

        cv2.namedWindow("image", cv2.WINDOW_NORMAL)
        cv2.imshow('image', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    @staticmethod
    def _get_grab_params(location):
        """
        Args:
            location:
        """
        return {
            "top": location.y1,
            "left": location.x1,
            "width": location.x2 - location.x1,
            "height": location.y2 - location.y1
        }
