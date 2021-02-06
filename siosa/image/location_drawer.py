import logging

import cv2.cv2 as cv2
import mss
import mss.tools
import numpy as np
from PIL import Image
from siosa.location.location_factory import LocationFactory, Locations


class LocationDrawer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    @staticmethod
    def draw(location):
        """
        Draws the given location on screen
        Args:
            location: The location of the screen to draw a rectangle on.
        """

        # The screen part to capture
        image = None

        lf = LocationFactory()
        full_screen_grab_params = LocationDrawer._get_grab_params(
            lf.get(Locations.FULL_SCREEN))
        with mss.mss() as sct:
            image = sct.grab(full_screen_grab_params)

        image_bytes_rgb = Image.frombytes(
            'RGB',
            (lf.resolution.w, lf.resolution.h),
            image.rgb)

        image_bytes_bgr = cv2.cvtColor(
            np.array(image_bytes_rgb), cv2.COLOR_RGB2BGR)
        cv2.rectangle(image_bytes_bgr, (location.x1, location.y1), (location.x2, location.y2), (0, 0, 255), 4)

        image_bytes_bgr = cv2.resize(image_bytes_bgr,  (lf.resolution.w//2, lf.resolution.h//2))

        cv2.imshow('image', image_bytes_bgr)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    @staticmethod
    def _get_grab_params(location):
        return {
            "top": location.y1,
            "left": location.x1,
            "width": location.x2 - location.x1,
            "height": location.y2 - location.y1
        }
