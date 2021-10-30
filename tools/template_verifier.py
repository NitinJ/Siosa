import logging
import os

import pyautogui
from cv2 import cv2

from siosa.common.decorations import override
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.in_game_location import InGameLocation
from siosa.location.location_factory import LocationFactory, Locations
from siosa.location.resolution import Resolution

FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
logging.basicConfig(format=FORMAT)


class ImageTemplateMatcher(TemplateMatcher):
    def __init__(self, template, image_path, location):
        self.image = self.crop_image(cv2.imread(image_path), location)
        super().__init__(template, threshold=0.8, debug=True)

    def crop_image(self, image, location):
        x1 = location.x1
        y1 = location.y1
        x2 = location.x2
        y2 = location.y2
        cropped_img = image[y1:y2, x1:x2]
        return cropped_img

    @override
    def get_image_for_location(self, location: InGameLocation):
        return self.image


def get_location_factory(image_path):
    if not image_path:
        return LocationFactory()
    image = cv2.imread(image_path)
    h, w = image.shape[0:2]
    return LocationFactory(resolution=Resolution(w, h))


if __name__ == "__main__":
    # If set to None, takes image from the screen
    image_path = 'images/tradeexalt.PNG'
    lf = get_location_factory(image_path)

    # Params
    template = TemplateRegistry.get_template_for_currency_stack('chaos', 3).get()
    match_location = lf.get(Locations.TRADE_WINDOW_OTHER)

    # Matching
    tm = None
    if image_path and os.path.exists(image_path):
        tm = ImageTemplateMatcher(template, image_path, match_location)
    else:
        pyautogui.confirm(
            text='Press OK to verify template({}) on location({})'.format(
                template,
                match_location),
            title='Grab template',
            buttons=['OK'])
        tm = TemplateMatcher(template, debug=True)
    print(tm.match(match_location))

