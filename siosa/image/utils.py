import mss
import numpy as np
from PIL import Image
from cv2 import cv2

from siosa.control.window_controller import WindowController
from siosa.location.in_game_location import InGameLocation


def grab_screenshot(location: InGameLocation):
    """
    Returns a screenshot for the given in game location as a cv2 usable image.
    Args:
        location:

    Returns:

    """
    sct = mss.mss()
    image_location = {
        "mon": str(WindowController().get_mss_monitor()),
        "top": location.y1,
        "left": location.x1,
        "width": location.x2 - location.x1,
        "height": location.y2 - location.y1
    }
    image = sct.grab(image_location)
    return np.array(Image.frombytes('RGB',
                           (image_location['width'], image_location['height']),
                           image.rgb))


def threshold(img):
    img2 = cv2.bilateralFilter(img, 1, 4, 4)
    ret, thresh = cv2.threshold(img2, 120, 255, cv2.THRESH_TOZERO)
    return thresh


def normalize(img):
    norm_img = np.zeros((800, 800))
    return cv2.normalize(img, norm_img, 0, 255, cv2.NORM_MINMAX)


def grayscale(img):
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
