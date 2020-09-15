import copy
import logging

import cv2
import mss
import numpy as np
import pyautogui
import pytesseract
from PIL import Image
from pytesseract import Output

from siosa.image.template import Template
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import LocationFactory, Locations

lf = LocationFactory()

FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=FORMAT)

# get grayscale image
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# noise removal
def remove_noise(image):
    return cv2.medianBlur(image, 5)


# thresholding
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_OTSU)[1]


# dilation
def dilate(image):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.dilate(image, kernel, iterations=1)


# erosion
def erode(image):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.erode(image, kernel, iterations=1)


# opening - erosion followed by dilation
def opening(image):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)


# canny edge detection
def canny(image):
    return cv2.Canny(image, 100, 200)


# skew correction
def deskew(image):
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
    return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)


def show_image(image):
    cv2.imshow('image', image)
    cv2.waitKey(0)


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
    return cv2.cvtColor(
        np.array(image_bytes_rgb), cv2.COLOR_RGB2BGR)


class OCR:
    @staticmethod
    def clahe(img, clip_limit=2.0, grid_size=(8, 8)):
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=grid_size)
        return clahe.apply(img)

    @staticmethod
    def getFilteredImage(src):
        srcH, srcW = src.shape[:2]
        src = cv2.resize(src, (int(srcW * 1.5), int(srcH * 1.5)))

        # HSV thresholding to get rid of as much background as possible
        hsv = cv2.cvtColor(src.copy(), cv2.COLOR_BGR2HSV)
        # show_image(hsv)
        # Original
        # lower_blue = np.array([0, 0, 180])
        # upper_blue = np.array([180, 38, 255])

        # Best
        # lower_blue = np.array([0, 0, 97])
        # upper_blue = np.array([0, 0, 255])

        lower_blue = np.array([0, 0, 97])
        upper_blue = np.array([0, 20, 255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        result = cv2.bitwise_and(src, src, mask=mask)
        b, g, r = cv2.split(result)
        g = OCR.clahe(g, 5, (5, 5))
        inverse = cv2.bitwise_not(g)
        return inverse


if __name__ == "__main__":
    pyautogui.confirm(
        text='Press OK to grab image on location({})'.format(
            lf.get(Locations.INVENTORY)),
        title='Grab image',
        buttons=['OK'])

    image = get_image(lf.get(Locations.INVENTORY))
    image_filtered = OCR.getFilteredImage(image)
    show_image(image_filtered)
    # cv2.imwrite("17.png", image)

    custom_config = r'-c tessedit_char_whitelist=0123456789 --oem 3 --psm 6 digits'
    d = pytesseract.image_to_data(image_filtered, config=custom_config,
                                  lang='poe',
                                  output_type=Output.DICT)
    print(d)
    for i in range(0, len(d['conf'])):
        print(d['conf'][i], d['text'][i])

    n_boxes = len(d['text'])
    for i in range(n_boxes):
        if int(d['conf'][i]) > 70:
            (x, y, w, h) = (
                d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    show_image(image)