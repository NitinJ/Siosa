import logging

import cv2
import mss
import numpy
import numpy as np
import pyautogui
import pytesseract
from PIL import Image
from pytesseract import Output
import matplotlib.pyplot as plt
from skimage import morphology
import numpy as np
import skimage

from siosa.image.template import Template
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location import Location
from siosa.location.location_factory import LocationFactory, Locations
from siosa.location.resolution import Resolutions
from imutils.perspective import four_point_transform

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
        np.array(image_bytes_rgb), cv2.COLOR_RGB2BGR)


class OCR:
    @staticmethod
    def clahe(img, clip_limit=0.1, grid_size=(1, 1)):
        """
        Args:
            img:
            clip_limit:
            grid_size:
        """
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=grid_size)
        return clahe.apply(img)

    @staticmethod
    def getFilteredImage0(src):
        """
        Args:
            src:
        """
        srcH, srcW = src.shape[:2]

        blured1 = cv2.medianBlur(src, 51)
        show_image(blured1)

        blured2 = cv2.medianBlur(src, 3)
        show_image(blured2)

        divided = np.ma.divide(blured1, blured2).data
        normed = np.uint8(255 * divided / divided.max())
        th, threshed = cv2.threshold(normed, 98, 255, cv2.THRESH_OTSU)

        show_image(threshed)
        return threshed

    @staticmethod
    def getFilteredImage(src):
        """
        Args:
            src:
        """
        srcH, srcW = src.shape[:2]
        src = cv2.resize(src, (int(srcW * 1.2), int(srcH * 1.2)))

        hsv = cv2.cvtColor(src.copy(), cv2.COLOR_BGR2HSV)
        # HSV thresholding to get rid of as much background as possible
        hsv = cv2.cvtColor(src.copy(), cv2.COLOR_BGR2HSV)

        # show_image(hsv, 'hsv')

        # Original
        lower_blue = np.array([0, 0, 97])
        upper_blue = np.array([220, 20, 255])

        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        result = cv2.bitwise_and(src, src, mask=mask)

        # show_image(result, 'result')

        b, g, r = cv2.split(result)

        # show_image(g)
        g = OCR.clahe(g)
        inverse = cv2.bitwise_not(g)

        show_image(inverse, 'inverse')
        return inverse

    @staticmethod
    def getFilteredImage2(src):
        """
        Args:
            src:
        """
        image = OCR.getFilteredImage(src)

        # Find contours and remove small noise
        cnts = cv2.findContours(image, cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        for c in cnts:
            area = cv2.contourArea(c)
            if area < 10:
                cv2.drawContours(image, [c], -1, 0, -1)

        show_image(image, 'Final result')
        return image

    def remove_small_objects(img, min_size=100):
        """
        Args:
            min_size:
        """
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 2))
        opening = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

        result = 255 - opening
        cv2.imshow('thresh', img)
        cv2.imshow('opening', opening)
        cv2.imshow('result', result)
        return result

    @staticmethod
    def getFilteredImage3(img):
        """
        Args:
            img:
        """
        mask = np.zeros(img.shape, np.uint8)
        sx = 18
        sy = 18

        w = 52
        h = 52

        for i in range(0, 12):
            for j in range(0, 5):
                xi = sx + i*w
                yi = sy + j*h
                mask[yi:yi + sx, xi:xi + sy] = img[yi:yi + sx, xi:xi + sy]

        show_image(mask, "MASK")
        return mask

    @staticmethod
    def removeSmallObjects(img):
        # find all your connected components (white blobs in your image)
        """
        Args:
            img:
        """
        nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(
            img, connectivity=4)
        # connectedComponentswithStats yields every seperated component with information on each of them, such as size
        # the following part is just taking out the background which is also considered a component, but most of the time we don't want that.
        sizes = stats[1:, -1]
        nb_components = nb_components - 1

        # minimum size of particles we want to keep (number of pixels)
        # here, it's a fixed value, but you can set it as you want, eg the mean of the sizes or whatever
        min_size = 10

        # your answer image
        img2 = np.zeros((output.shape))
        # for every component in the image, you keep it only if it's above min_size
        for i in range(0, nb_components):
            if sizes[i] >= min_size:
                img2[output == i + 1] = 255
        show_image(img2)

    @staticmethod
    def thresholding(img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # applying different thresholding
        # techniques on the input image
        # all pixels value above 120 will
        # be set to 255

        img1 = cv2.GaussianBlur(img, (1, 1), 0)
        cv2.imshow('blur1', img1)

        img2 = cv2.bilateralFilter(img, 4, 20, 20)
        cv2.imshow('blur2', img)


        ret, thresh4 = cv2.threshold(img1, 120, 255, cv2.THRESH_TOZERO)
        cv2.imshow('Set to 0', thresh4)

        ret, thresh4 = cv2.threshold(img2, 120, 255, cv2.THRESH_TOZERO)
        cv2.imshow('Set to 1', thresh4)
        # the window showing output images
        # with the corresponding thresholding
        # techniques applied to the input images

        # De-allocate any associated memory usage
        if cv2.waitKey(0) & 0xff == 27:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    image = get_image(lf.get(Locations.SCREEN_FULL))
    # stash_template = Template.from_registry(TemplateRegistry.STASH)
    # image, grayscale_image = stash_template.get()
    show_image(image)

    image = OCR.thresholding(image)
    # image = OCR.getFilteredImage(image)
    # image = OCR.getFilteredImage0(image)
    # image = OCR.removeSmallObjects(image)

    # image = OCR.remove_small_objects(image)
    show_image(image, 'FILTERED IMAGE MAIN')

    custom_config = r'-c tessedit_char_whitelist=0123456789 --oem 3 --psm 6 digits'
    d = pytesseract.image_to_data(image, config=custom_config,
                                  lang='poe',
                                  output_type=Output.DICT)
    print(d)
    for i in range(0, len(d['conf'])):
        print(d['conf'][i], d['text'][i])

    # n_boxes = len(d['text'])
    # for i in range(n_boxes):
    #     if int(d['conf'][i]) > 80:
    #         (x, y, w, h) = (
    #             d['left'][i], d['top'][i], d['width'][i], d['height'][i])
    #         image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    # show_image(image, 'WITH BOXES')
