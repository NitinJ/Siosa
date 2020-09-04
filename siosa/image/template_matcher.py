import copy
import logging
import time

import cv2.cv2 as cv2
import mss
import mss.tools
import numpy as np
from PIL import Image

from siosa.control.window_controller import WindowController


class TemplateMatcher:
    def __init__(self, template, confidence=0.75, debug=False):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.sct = mss.mss()
        self.debug = debug
        self.confidence = confidence
        self.template = template

    def match(self, location):
        """
        Matches the template on a given screen location.
        Args:
            location: The location of the screen to match template with.

        Returns:
            The positions (relative to the location) of matches with template.
        """
        if not WindowController().is_poe_in_foreground():
            self.logger.error("POE is not in foreground to capture template.")
            raise (Exception("Path of Exile is not in foreground"))

        # The screen part to capture
        ts1 = time.time()
        screen_location = TemplateMatcher._get_grab_params(location)
        image = self.sct.grab(screen_location)
        image_bytes_rgb = Image.frombytes(
            'RGB',
            (screen_location['width'], screen_location['height']),
            image.rgb)
        image_bytes_bgr = cv2.cvtColor(
            np.array(image_bytes_rgb), cv2.COLOR_RGB2BGR)
        image_bytes_bgr_copy = copy.copy(image_bytes_bgr)
        image_bytes_gray = cv2.cvtColor(image_bytes_bgr, cv2.COLOR_BGR2GRAY)

        template = self.template.get()
        if self.debug:
            cv2.imshow('image', template)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        tmin, tmax = self._get_bgr_min_max(template)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        template_width, template_height = template_gray.shape[::-1]

        # Match the template
        match_result = cv2.matchTemplate(
            image_bytes_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        match_locations = np.where(match_result >= self.confidence)

        points = []
        for point in zip(*match_locations[::-1]):
            cropped_img = image_bytes_bgr_copy[point[1]:point[1] +
                                                        template_height,
                          point[0]:point[0] + template_width]
            dmin, dmax = self._get_bgr_min_max(cropped_img)
            if dmin[0] <= tmin[0] and dmin[1] <= tmin[1] and dmin[2] <= tmin[2]:
                pt = (point[0] + template_width // 2,
                      point[1] + template_height // 2)
                cv2.rectangle(image_bytes_bgr, pt, pt, (0, 0, 255), 4)
                points.append(pt)

        self.logger.info("Template matcher took {}".format(time.time() - ts1))

        if self.debug:
            cv2.imshow('image', image_bytes_bgr)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return points

    @staticmethod
    def _get_grab_params(location):
        return {
            "top": location.y1,
            "left": location.x1,
            "width": location.x2 - location.x1,
            "height": location.y2 - location.y1
        }

    @staticmethod
    def _get_bgr_min_max(img):
        min_ch = (np.amin(img[:, :, 0]), np.amin(
            img[:, :, 1]), np.amin(img[:, :, 2]))
        max_ch = (np.amax(img[:, :, 0]), np.amax(
            img[:, :, 1]), np.amax(img[:, :, 2]))
        return min_ch, max_ch
