from cv2 import cv2

from siosa.common.decorations import override
from siosa.image.template import Template
from siosa.image.utils import threshold, grayscale, normalize
from siosa.location.resolution import Resolution
import numpy as np


# dilation
def dilate(image):
    """
    Args:
        image:
    """
    kernel = np.ones((5, 5), np.uint8)
    return cv2.dilate(image, kernel, iterations=3)


class AcceptAuraTemplate(Template):
    def __init__(self, template_name, template_file_path,
                 resolution: Resolution):
        super().__init__(template_name, template_file_path, resolution)

    @override
    def process_image(self, image):
        # Convert to hsv, create a mask for green color and dilate + threshold.
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, (53, 157, 31), (83, 255, 255))
        img = dilate(threshold(mask))
        return img
