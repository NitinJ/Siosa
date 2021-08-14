import logging
import time

import cv2.cv2 as cv2
import mss
import mss.tools
import numpy as np
import pyautogui
from PIL import Image

from siosa.control.window_controller import WindowController
from siosa.location.in_game_location import InGameLocation


class TemplateMatcher:
    def __init__(self, template, confidence=0.75, debug=False, scale=1.0):
        """
        Args:
            template:
            confidence:
            debug:
            scale:
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.wc = WindowController()
        self.debug = debug
        self.confidence = confidence
        self.template = template
        self.image_cache = {}
        self.scale = scale

    def get_image(self, screen_location, reuse):
        """
        Args:
            screen_location:
            reuse:
        """
        key = str(screen_location)
        if reuse and key in self.image_cache.keys():
            self.logger.info("Screen location image found in cache. Reusing.")
            return self.image_cache[key]

        image = None
        with mss.mss() as sct:
            image = sct.grab(screen_location)

        width = screen_location['width']
        height = screen_location['height']
        image_bytes_rgb = Image.frombytes('RGB', (width, height), image.rgb)
        image_bytes_rgb = image_bytes_rgb.resize(
            (int(width * self.scale), int(height * self.scale)))

        image_bytes_bgr = cv2.cvtColor(
            np.array(image_bytes_rgb), cv2.COLOR_RGB2BGR)
        image_bytes_gray = cv2.cvtColor(
            np.array(image_bytes_bgr), cv2.COLOR_RGB2GRAY)

        self.image_cache[key] = [image_bytes_bgr, image_bytes_gray]
        return self.image_cache[key]

    def _check_if_poe_is_in_foreground(self):
        ts1 = time.time()
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
        ts1 = time.time()
        if self.debug:
            self._check_if_poe_is_in_foreground()

        # Params for the part of the screen to capture.
        screen_location = TemplateMatcher._get_grab_params(
            location, self.wc.get_mss_monitor())
        image_bytes_bgr, image_bytes_gray = \
            self.get_image(screen_location, reuse)

        template, template_gray = self.template.get()
        if self.debug:
            cv2.imshow('template_gray', template_gray)
            cv2.imshow('image_bytes_gray', image_bytes_gray)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        tmin, tmax = self._get_bgr_min_max(template)
        template_width, template_height = template_gray.shape[::-1]

        # Match the template
        match_result = cv2.matchTemplate(
            image_bytes_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        match_locations = np.where(match_result >= self.confidence)

        points = []
        for point in zip(*match_locations[::-1]):
            cropped_img = image_bytes_bgr[point[1]:point[1] +
                                                   template_height,
                          point[0]:point[0] + template_width]
            dmin, dmax = self._get_bgr_min_max(cropped_img)
            if dmin[0] <= tmin[0] and dmin[1] <= tmin[1] and dmin[2] <= tmin[2]:
                pt = (point[0] + template_width // 2,
                      point[1] + template_height // 2)
                if self.debug:
                    cv2.rectangle(image_bytes_bgr, pt, pt, (0, 0, 255), 4)
                points.append(pt)

        if self.debug and points:
            cv2.imshow('image', image_bytes_bgr)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        self.logger.debug(
            "TemplateMatcher:{}, time:{} ms, npoints: {}".format(
                self.template.get_template_name(), (time.time() - ts1) * 1000,
                len(points)))
        return points

    @staticmethod
    def _get_grab_params(location, monitor):
        """
        Args:
            location:
        """
        return {
            "mon": str(monitor),
            "top": location.y1,
            "left": location.x1,
            "width": location.x2 - location.x1,
            "height": location.y2 - location.y1
        }

    @staticmethod
    def _get_bgr_min_max(img):
        """
        Args:
            img:
        """
        min_ch = (np.amin(img[:, :, 0]), np.amin(
            img[:, :, 1]), np.amin(img[:, :, 2]))
        max_ch = (np.amax(img[:, :, 0]), np.amax(
            img[:, :, 1]), np.amax(img[:, :, 2]))
        return min_ch, max_ch
