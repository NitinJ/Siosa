import copy
import logging
import os
import time

import cv2.cv2 as cv2
import mss
import mss.tools
import numpy as np
from PIL import Image

from siosa.control.window_controller import WindowController


class TemplateMatcher:
    def __init__(self, template_location, confidence=0.75, debug=False):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.sct = mss.mss()
        self.debug = debug
        self.confidence = confidence
        self.template_location = template_location
        if self.debug:
            time.sleep(2)

    def match(self, location):
        if not WindowController().is_poe_in_foreground():
            self.logger.error("POE is not in foreground to capture template.")
            raise(Exception("Path of Exile is not in foreground"))

        self.template_file_path = self._create_template(self.template_location)

        # The screen part to capture
        ts1 = time.time()
        screen_location = self._get_grab_params(location)
        image = self.sct.grab(screen_location)
        image_bytes_rgb = Image.frombytes(
            'RGB',
            (screen_location['width'], screen_location['height']),
            image.rgb)
        image_bytes_bgr = cv2.cvtColor(
            np.array(image_bytes_rgb), cv2.COLOR_RGB2BGR)
        image_bytes_bgr_copy = copy.copy(image_bytes_bgr)
        image_bytes_gray = cv2.cvtColor(image_bytes_bgr, cv2.COLOR_BGR2GRAY)

        template = cv2.imread(self.template_file_path)

        tmin, tmax = self._getBGRMinMax(template)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        template_width, template_height = template_gray.shape[::-1]

        # Match the template
        match_result = cv2.matchTemplate(
            image_bytes_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        match_locations = np.where(match_result >= self.confidence)

        points = []
        for point in zip(*match_locations[::-1]):
            cropedImg = image_bytes_bgr_copy[point[1]:point[1] +
                                             template_height, point[0]:point[0] + template_width]
            dmin, dmax = self._getBGRMinMax(cropedImg)
            if dmin[0] <= tmin[0] and dmin[1] <= tmin[1] and dmin[2] <= tmin[2]:
                pt = (point[0] + template_width//2,
                      point[1] + template_height//2)
                cv2.rectangle(image_bytes_bgr, pt, pt, (0, 0, 255), 4)
                points.append(pt)

        self.logger.info("Template matcher took {}".format(time.time() - ts1))

        if self.debug:
            cv2.imshow('image', image_bytes_bgr)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return points

    def _get_grab_params(self, location):
        return {
            "top": location.y1,
            "left": location.x1,
            "width": location.x2-location.x1,
            "height": location.y2-location.y1
        }

    def _get_template_output_file_path(self, name):
        def parent(f): return os.path.dirname(os.path.abspath(f))
        resources = os.path.join(parent(parent(__file__)), "resources")
        templates = os.path.join(resources, "templates")
        return os.path.join(templates, name)

    def _create_template(self, location):
        image_location = self._get_grab_params(location)
        output_file_path = self._get_template_output_file_path(
            "sct-{top}x{left}_{width}x{height}.png".format(**image_location))

        if os.path.isfile(output_file_path):
            self.logger.info(
                'Template already exists at {}'.format(output_file_path))
            return output_file_path

        image = self.sct.grab(image_location)
        image_bytes_rgb = Image.frombytes(
            'RGB',
            (image_location['width'], image_location['height']),
            image.rgb)
        image_bytes_bgr = cv2.cvtColor(
            np.array(image_bytes_rgb), cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_file_path, image_bytes_bgr)
        self.logger.debug('Created template at: {}'.format(output_file_path))
        return output_file_path

    def _getBGRMinMax(self, img):
        min_ch = (np.amin(img[:, :, 0]), np.amin(
            img[:, :, 1]), np.amin(img[:, :, 2]))
        max_ch = (np.amax(img[:, :, 0]), np.amax(
            img[:, :, 1]), np.amax(img[:, :, 2]))
        return min_ch, max_ch
