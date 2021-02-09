import logging
import os

import cv2.cv2 as cv2
import numpy as np
import mss
import mss.tools
from PIL import Image

from siosa.location.location_factory import LocationFactory
from siosa.location.resolution import Resolution

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Template:
    def __init__(self, template_file_name, resolution):
        """
        Args:
            template_file_name: Name of the template image file.
            resolution: Resolution in which the template file has been created.
        """
        self.template_file_name = template_file_name
        self.resolution = resolution
        self.resized_template = self._get_resized_template()
        self.template_gray = cv2.cvtColor(self.resized_template, cv2.COLOR_BGR2GRAY)

    def get_template_name(self):
        return self.template_file_name

    def _get_resized_template(self):
        """
        Returns the template image resized to the current screen resolution.
        Returns:
            The resized template.
        """
        template = cv2.imread(
            Template._get_template_file_path(self.template_file_name))
        lf = LocationFactory()
        dim = (int(template.shape[1] * (lf.resolution.w / self.resolution.w)),
               int(template.shape[0] * (lf.resolution.h / self.resolution.h)))

        # Resize template to the current resolution.
        return cv2.resize(template, dim, interpolation=cv2.INTER_AREA)

    def get(self):
        """
        Returns the template image resized to the current screen resolution.
        Returns:
            The resized template.
        """
        return self.resized_template, self.template_gray

    @staticmethod
    def create(name, location, overwrite=False, debug=False):
        """
        Creates a template with a given name by capturing screen at the given
        location.
        Args:
            name: Name of the file, in which template image will be stored.
            location: Screen location to capture and create template from.
            overwrite: Whether to overwrite the template file if it already
                exists.

        Returns:
            The full template file path
        """
        sct = mss.mss()
        image_location = Template._get_grab_params(location)
        output_file_path = Template._get_template_file_path(
            "sct-tmp-{}.png".format(name))

        if os.path.isfile(output_file_path):
            logger.info(
                'Template already exists at {}'.format(output_file_path))
            if not overwrite:
                return output_file_path

        image = sct.grab(image_location)
        image_bytes_rgb = Image.frombytes(
            'RGB',
            (image_location['width'], image_location['height']),
            image.rgb)

        if debug:
            cv2.imshow('Template', np.array(image_bytes_rgb))
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        image_bytes_bgr = cv2.cvtColor(
            np.array(image_bytes_rgb), cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_file_path, image_bytes_bgr)
        logger.debug('Created template at: {}'.format(output_file_path))
        return output_file_path

    @staticmethod
    def from_registry(template_registry):
        return Template(
            template_registry[0],
            Resolution(template_registry[1][0], template_registry[1][1]))

    @staticmethod
    def _get_grab_params(location):
        return {
            "top": location.y1,
            "left": location.x1,
            "width": location.x2 - location.x1,
            "height": location.y2 - location.y1
        }

    @staticmethod
    def _get_template_file_path(name):
        """
        Returns the template output file path given name of the template.
        Args:
            name: Name of the template

        Returns:
            Full file path of the template file.
        """
        def parent(f): return os.path.dirname(os.path.abspath(f))

        resources = os.path.join(parent(parent(__file__)), "resources")
        templates = os.path.join(resources, "templates")
        return os.path.join(templates, name)
