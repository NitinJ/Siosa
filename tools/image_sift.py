import logging
import time

import cv2
import matplotlib.pyplot as plt
import mss
import numpy as np
from PIL import Image

from siosa.image.template import Template
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import LocationFactory, Locations
from siosa.location.resolution import Resolution

lf = LocationFactory()

FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=FORMAT)


# get grayscale image
def get_grayscale(image):
    """
    Args:
        image:
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# noise removal
def remove_noise(image):
    """
    Args:
        image:
    """
    return cv2.medianBlur(image, 5)


# thresholding
def thresholding(image):
    """
    Args:
        image:
    """
    return cv2.threshold(image, 0, 255, cv2.THRESH_OTSU)[1]


# dilation
def dilate(image):
    """
    Args:
        image:
    """
    kernel = np.ones((5, 5), np.uint8)
    return cv2.dilate(image, kernel, iterations=1)


# erosion
def erode(image):
    """
    Args:
        image:
    """
    kernel = np.ones((5, 5), np.uint8)
    return cv2.erode(image, kernel, iterations=1)


# opening - erosion followed by dilation
def opening(image):
    """
    Args:
        image:
    """
    kernel = np.ones((5, 5), np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)


# canny edge detection
def canny(image):
    """
    Args:
        image:
    """
    return cv2.Canny(image, 100, 200)


# skew correction
def deskew(image):
    """
    Args:
        image:
    """
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC,
                             borderMode=cv2.BORDER_REPLICATE)
    return rotated


# template matching
def match_template(image, template):
    """
    Args:
        image:
        template:
    """
    return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)


def show_image(image, name='image'):
    """
    Args:
        image:
        name:
    """
    cv2.imshow(name, image)
    cv2.waitKey(0)


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


def sift(img1, img2):
    # sift
    ts = time.time()
    sift = cv2.xfeatures2d.SIFT_create()

    keypoints_1, descriptors_1 = sift.detectAndCompute(img1, None)
    keypoints_2, descriptors_2 = sift.detectAndCompute(img2, None)

    print(len(keypoints_1), len(keypoints_2))

    # feature matching
    bf = cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)

    matches = bf.match(descriptors_1, descriptors_2)
    matches = sorted(matches, key=lambda x: x.distance)

    good_matches = matches[:5]
    for match in good_matches:
        print(match.distance)
    print(len(matches))

    img3 = cv2.drawMatches(img1, keypoints_1, img2, keypoints_2, good_matches,
                           img2, flags=2)
    cv2.imshow('img3', img3)
    cv2.waitKey(0)
    # plt.imshow(img3), plt.show()
    print(time.time() - ts)


def canny_source():
    img = get_image(lf.get(Locations.SCREEN_FULL))
    img = cv2.bilateralFilter(img, 4, 20, 20)
    edges = cv2.Canny(img, 150, 200)
    plt.subplot(121), plt.imshow(img, cmap='gray')
    plt.title('Original Image'), plt.xticks([]), plt.yticks([])
    plt.subplot(122), plt.imshow(edges, cmap='gray')
    plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
    plt.show()


def get_thresholded_image(img):
    img2 = cv2.bilateralFilter(img, 4, 20, 20)
    ret, thresh = cv2.threshold(img2, 120, 255, cv2.THRESH_TOZERO)
    return thresh


def normalize(img):
    norm_img = np.zeros((800, 800))
    return cv2.normalize(img, norm_img, 0, 255, cv2.NORM_MINMAX)


def get_image_from_path(image_path, lf, template):
    image_bytes_bgr = normalize(cv2.imread(image_path))
    image_bytes_bgr = normalize(image_bytes_bgr)
    image_bytes_gray = cv2.cvtColor(image_bytes_bgr, cv2.COLOR_BGR2GRAY)
    return resize_image(template, image_bytes_gray, lf.resolution, lf.resolution.w, lf.resolution.h)


def resize_image(template, image_bytes, image_resolution, image_width,
                  image_height):
    height_factor = (template.resolution.h / image_resolution.h)
    width_factor = (template.resolution.w / image_resolution.w)
    new_w = int(image_width * width_factor)
    new_h = int(image_height * height_factor)
    return cv2.resize(image_bytes, (new_w, new_h), interpolation=cv2.INTER_AREA)


def crop_image(img, location):
    x1 = location.x1
    y1 = location.y1
    x2 = location.x2
    y2 = location.y2
    cropped_img = img[y1:y2, x1:x2]
    cv2.imshow('cropped_img', cropped_img)
    cv2.waitKey(0)
    return cropped_img


if __name__ == "__main__":
    # pyautogui.confirm(
    #     text='Press OK to grab image',
    #     title='Grab image',
    #     buttons=['OK'])

    # lf = LocationFactoryBase(Resolutions.p1080)
    image_path = 'images/accepting_trade.png'
    lf = LocationFactory(resolution=Resolution(2560, 1440))
    # img = get_thresholded_image(get_image(lf.get(Locations.SCREEN_FULL)))
    # img = get_thresholded_image(get_image(lf.get(Locations.SCREEN_FULL)))

    # img = get_image(lf.get(Locations.SCREEN_FULL))
    location = lf.get(Locations.TRADE_WINDOW_FULL)
    template = \
    Template.from_registry(TemplateRegistry.TRADE_WINDOW_ME_EMPTY_TEXT)
    img = crop_image(get_image_from_path(image_path, lf, template), location)

    sift(img, template.get()[1])
    # cv2.imwrite('filtered_image.jpg', image)
    # canny_source()
