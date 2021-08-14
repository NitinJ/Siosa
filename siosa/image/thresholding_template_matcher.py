import numpy as np
from cv2 import cv2

from siosa.image.reusable_template_matcher import ReusableTemplateMatcher


def get_thresholded_image(img):
    img2 = cv2.bilateralFilter(img, 4, 20, 20)
    ret, thresh = cv2.threshold(img2, 120, 255, cv2.THRESH_TOZERO)
    return thresh


class ThresholdingTemplateMatcher(ReusableTemplateMatcher):
    """
    This matcher matches templates by first thresholding the screen location.
    """

    def __init__(self, location, debug=False, scale=1.0):
        """
        Args:
            location:
            debug:
            scale:
        """
        ReusableTemplateMatcher.__init__(self, location, confidence=0.88,
                                         debug=debug,
                                         scale=scale)

    def get_image(self, screen_location, reuse):
        """
        Args:
            screen_location:
            reuse:
        """
        image_bytes_bgr, image_bytes_gray = \
            super().get_image(screen_location, reuse)
        image_bytes_bgr = get_thresholded_image(image_bytes_bgr)
        image_bytes_gray = get_thresholded_image(image_bytes_gray)
        if self.debug:
            cv2.imshow('image_bytes_bgr', image_bytes_bgr)
            cv2.imshow('image_bytes_gray', image_bytes_gray)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        return image_bytes_bgr, image_bytes_gray
