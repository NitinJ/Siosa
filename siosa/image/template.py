import logging

import cv2.cv2 as cv2

from siosa.image.utils import grayscale
from siosa.location.location_factory import LocationFactory
from siosa.location.resolution import Resolution

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Template:
    def __init__(self, template_name, template_file_path,
                 resolution: Resolution):
        """
        Args:
            template_file_path: Path of the template image file.
        """
        self.template_name = template_name
        self.template_file_path = template_file_path
        self.resolution = resolution
        self.lf = LocationFactory()

        template_image = cv2.imread(self.template_file_path)
        self.template = self._process_template(template_image)

    def _process_template(self, template_image):
        return self.process_image(template_image)

    def process_image(self, image):
        """
        Processes an image to be matched against the template. This should be
        the image that is to be matched against the template image stored.
        Args:
            image:

        Returns: Gray scale normalized image.

        """
        return grayscale(image)

    def get_dimensions(self):
        """Returns: Returns the dimensions of the template in 1080p resolution
        and not in the current resolution.
        """
        h, w = self.template.shape[:2]
        return [w, h]

    def get(self, scale=1.0):
        """Returns the template image scaled by the given factor.
        """
        w, h = self.get_dimensions()
        height_new = int(h * scale)
        width_new = int(w * height_new / h)

        # No need to process template here as it's already stored processed.
        return cv2.resize(self.template, (width_new, height_new),
                          interpolation=cv2.INTER_AREA)
