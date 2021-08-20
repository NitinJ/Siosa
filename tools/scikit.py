import logging
import time

import mss
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from cv2 import cv2
from scipy import ndimage
from scipy.ndimage import filters

from skimage import data
from skimage.feature import match_template, peak_local_max

from siosa.image.scikit_template_matcher import ScikitTemplateMatcher
from siosa.image.template import Template
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.in_game_location import InGameLocation
from siosa.location.location_factory import LocationFactory, Locations
from siosa.location.resolution import Resolution
from skimage.io import imread, imshow


FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=FORMAT)


def find_all(image, template, result):
    template_width, template_height = template.shape
    plt.figure(num=None, figsize=(16, 9), dpi=80)
    z = []
    for x, y in peak_local_max(result, threshold_abs=0.75, exclude_border=8):
        z.append((y, x))
        rect = plt.Rectangle((y, x), template_height, template_width,
                             color='r', fc='none')
        plt.gca().add_patch(rect)
    imshow(image)
    plt.show()
    print(z)


def plot(image, template, result):
    x, y = np.unravel_index(np.argmax(result), result.shape)
    template_width, template_height = template.shape

    fig = plt.figure('Debug', figsize=(12, 12), dpi=80)
    ax1 = plt.subplot(2, 2, 1)
    ax2 = plt.subplot(2, 2, 2)
    ax3 = plt.subplot(2, 2, 3)
    ax4 = plt.subplot(2, 2, 4, sharex=ax3, sharey=ax3)

    ax1.imshow(template, cmap=plt.cm.gray)
    ax1.set_axis_off()
    ax1.set_title('template')

    ax2.imshow(image, cmap=plt.cm.gray)
    ax2.set_axis_off()
    ax2.set_title('image')
    # ax2.autoscale(True)

    rect = plt.Rectangle((x, y), template_width, template_height, edgecolor='r',
                         facecolor='none')
    ax2.add_patch(rect)

    ax3.imshow(result)
    ax3.set_axis_off()
    # ax3.autoscale(True)
    ax3.set_title('match_template - result')

    ax4.imshow(image, cmap=plt.cm.gray)
    ax4.set_axis_off()
    ax4.set_title('match_template - all matches')
    # ax4.autoscale(True)
    for x, y in peak_local_max(result, threshold_abs=0.75, exclude_border=8):
        rect = plt.Rectangle(
            (y - template_width//2, x - template_height//2),
                             template_width, template_height,
                             edgecolor='r',
                             facecolor='none')
        ax4.add_patch(rect)

    plt.show()


def scikit(image, template):
    ts = time.time()
    result = match_template(image, template, pad_input=True, mode='edge')
    print(result.max())
    plot(image, template, result)
    find_all(image, template, result)
    print(time.time() - ts)

def normalize(img):
    norm_img = np.zeros((800, 800))
    return cv2.normalize(img, norm_img, 0, 255, cv2.NORM_MINMAX)


def get_image(location):
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
    return normalize(cv2.cvtColor(np.array(image_bytes_rgb), cv2.COLOR_RGB2GRAY))


def crop_image(img, location):
    x1 = location.x1
    y1 = location.y1
    x2 = location.x2
    y2 = location.y2
    cropped_img = img[y1:y2, x1:x2]
    return cropped_img


def resize_image(image_bytes):
    height_factor = (1080/1440)
    width_factor = (1920/2560)
    h, w, c = image_bytes.shape
    new_w = int(w * width_factor)
    new_h = int(h * height_factor)
    return cv2.resize(image_bytes, (new_w, new_h), interpolation=cv2.INTER_AREA)


def get_image_from_file(image_path, location):
    image = cv2.imread(image_path)
    image = crop_image(image, location)
    image = resize_image(image)
    return normalize(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))


def from_poe():
    lf = LocationFactory(resolution=Resolution(1920, 1080))
    location = lf.get(Locations.SCREEN_FULL)
    template = TemplateRegistry.STASH.get().get()
    scikit(get_image(location), template)


class ImageTm(TemplateMatcher):
    def __init__(self, image, template):
        self.image = image
        super().__init__(template, threshold=0.75, debug=True)

    def get_image(self, location: InGameLocation, reuse):
        """
        Args:
            location:
            reuse:
        """
        # Params for the part of the screen to capture.
        key = str(location)
        if reuse and key in self.image_cache.keys():
            self.logger.info(
                "Screen location image found in cache. Reusing.")
            return self.image_cache[key]

        image_rgb = self.image
        width = location.get_width()
        height = location.get_height()

        # Resize image down to the resolution of the template and save the
        # processed image in cache.
        image_rgb = self._resize_image(
            np.array(image_rgb), location.resolution, width, height)

        self.image_cache[key] = self.template.process_image(image_rgb)
        return self.image_cache[key]


def from_file():
    image_path = 'images/accepting_trade.png'
    lf = LocationFactory(resolution=Resolution(2560, 1440))
    # lf = LocationFactory(resolution=Resolution(3440, 1440))

    location = lf.get(Locations.TRADE_ACCEPT_GREEN_AURA_BOX)
    template = TemplateRegistry.TRADE_ACCEPT_GREEN_AURA.get()
    image = get_image_from_file(image_path, location)

    # res = ScikitTemplateMatcher(debug=True, threshold=0.75).match(image, template.get())
    # print(res)

    image = crop_image(cv2.imread(image_path), location)
    tm = ImageTm(image, template)
    res = tm.match(location)
    print(res)

# from_poe()
from_file()