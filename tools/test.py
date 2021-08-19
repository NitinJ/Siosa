import logging

import mss
from PIL import Image
from cv2 import cv2
import numpy as np
from siosa.image.template import Template
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.image.thresholding_template_matcher import \
    ThresholdingTemplateMatcher
from siosa.location.location_factory import LocationFactoryBase, \
    LocationFactory, Locations
from siosa.location.resolution import Resolution
from tools.image_template_matcher import ImageTemplateMatcher

FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"

logging.basicConfig(
    level=logging.INFO,
    format=FORMAT,
    handlers={
        logging.FileHandler('siosa.log', encoding='utf-8'),
        logging.StreamHandler()
    }
)

def get_image(location):
    """
    Args:
        location:
    """
    screen_location = {
        "top": location.y1,
        "left": location.x1,
        "width": location.x2 - location.x1,
        "height": location.y2 - location.y1
    }
    image = None
    with mss.mss() as sct:
        image = sct.grab(screen_location)
    image_bytes_rgb = Image.frombytes(
        'RGB',
        (screen_location['width'], screen_location['height']),
        image.rgb)
    return cv2.cvtColor(
        np.array(image_bytes_rgb), cv2.COLOR_RGB2GRAY)

def normalize(img):
    norm_img = np.zeros((800, 800))
    return cv2.normalize(img, norm_img, 0, 255, cv2.NORM_MINMAX)

def get_thresholded_image(img):
    img = normalize(img)
    img2 = cv2.bilateralFilter(img, 1, 4, 4)
    ret, thresh = cv2.threshold(img2, 120, 255, cv2.THRESH_TOZERO)
    # ret, thresh = cv2.threshold(img2, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # kernel = np.ones((1, 1), np.uint8)
    # thresh = cv2.dilate(thresh, kernel)
    return thresh

def from_file():
    image_path = 'images/currency.png'
    lf = LocationFactory(resolution=Resolution(2560, 1440))
    location = lf.get(Locations.SCREEN_FULL)
    template = Template.from_registry(
        TemplateRegistry.STASH_BANNER)
    # cv2.namedWindow("img", cv2.WND_PROP_FULLSCREEN)
    # cv2.setWindowProperty("img",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    # cv2.imshow('img', get_thresholded_image(get_image(location)))
    itm = ImageTemplateMatcher(location, image_path, template, debug=True)
    itm.match_stored()
    itm.show()

    # itm = TemplateMatcher(template, debug=True)
    # itm.match(location)
    cv2.waitKey(0)


def from_poe():
    lf = LocationFactory(resolution=Resolution(1920, 1080))
    location = lf.get(Locations.SCREEN_FULL)
    template = Template.from_registry(TemplateRegistry.GUILD_STASH)
    tm = ThresholdingTemplateMatcher(location, debug=True)
    tm.match_template(template)


from_file()
# from_poe()