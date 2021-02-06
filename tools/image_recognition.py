import logging

import cv2
import mss
import numpy as np
import pyautogui
import pytesseract
from PIL import Image
from pytesseract import Output

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


def show_image(image, name='image'):
    cv2.imshow(name, image)
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
        lower_blue = np.array([0, 0, 97])
        upper_blue = np.array([250, 20, 255])

        # Best
        # lower_blue = np.array([0, 0, 97])
        # upper_blue = np.array([0, 0, 255])

        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        result = cv2.bitwise_and(src, src, mask=mask)
        b, g, r = cv2.split(result)
        g = OCR.clahe(g, 5, (5, 5))
        inverse = cv2.bitwise_not(g)
        return inverse


    @staticmethod
    def labexpt(img):
        # -----Converting image to LAB Color model-----------------------------------
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        # cv2.imshow("lab", lab)

        # -----Splitting the LAB image to different channels-------------------------
        l, a, b = cv2.split(lab)
        # cv2.imshow('l_channel', l)
        # cv2.imshow('a_channel', a)
        # cv2.imshow('b_channel', b)

        # -----Applying CLAHE to L-channel-------------------------------------------
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        # cv2.imshow('CLAHE output', cl)

        # -----Merge the CLAHE enhanced L-channel with the a and b channel-----------
        limg = cv2.merge((cl, a, b))
        # cv2.imshow('limg', limg)

        # -----Converting image from LAB Color model to RGB model--------------------
        final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        # cv2.imshow('final', final)
        return final

    @staticmethod
    def getFilteredGrayImage(img):
        img = OCR.labexpt(img)
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        show_image(gray_image)
        # gray_image = cv2.inRange(gray_image, 10, 205)
        # gray_image = ~gray_image
        thresh = cv2.adaptiveThreshold(gray_image, 255, 1, 1, 11, 2)
        show_image(thresh, 'threash')
        # gray_image = cv2.medianBlur(gray_image, 5)
        # show_image(gray_image)

        gray_image = cv2.adaptiveThreshold(gray_image, 255,
                                           cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv2.THRESH_BINARY, 5, 2)
        ret, gray_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
        show_image(gray_image)

        contours,hierarchy = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        out = np.zeros(img.shape, np.uint8)
        for cnt in contours:
            # if cv2.contourArea(cnt) > 10 and cv2.contourArea(cnt) < 50:
            if True:
                [x, y, w, h] = cv2.boundingRect(cnt)
                if h > 28:
                    cv2.rectangle(thresh, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imshow('im', thresh)
        # cv2.imshow('out', out)
        cv2.waitKey(0)
        return gray_image


    @staticmethod
    def getFilteredImageGreen(src):
        src = OCR.labexpt(src)
        show_image(src, 'lab')
        srcH, srcW = src.shape[:2]
        src = cv2.resize(src, (int(srcW * 1.5), int(srcH * 1.5)))

        show_image(src)

        # HSV thresholding to get rid of as much background as possible
        hsv = cv2.cvtColor(src.copy(), cv2.COLOR_BGR2HSV)
        lower_blue = np.array([0, 0, 0])
        upper_blue = np.array([255, 20, 255])

        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        show_image(cv2.bitwise_and(src, src, mask=mask))
        show_image(255 - mask)
        result = cv2.bitwise_and(src, src, mask=mask)

        b, g, r = cv2.split(result)
        b = OCR.clahe(b, 5, (5, 5))
        inverse = cv2.bitwise_not(r)
        return inverse

def cleanup_text(text):
    return "".join([c if ord(c) < 128 else "" for c in text]).strip()

def detect_regions(image):
    reader = Reader(["en"], gpu=False)
    results = reader.readtext(image)

    # loop over the results
    for (bbox, text, prob) in results:
        # display the OCR'd text and associated probability
        print("[INFO] {:.4f}: {}".format(prob, text))
        # unpack the bounding box
        (tl, tr, br, bl) = bbox
        tl = (int(tl[0]), int(tl[1]))
        tr = (int(tr[0]), int(tr[1]))
        br = (int(br[0]), int(br[1]))
        bl = (int(bl[0]), int(bl[1]))
        text = cleanup_text(text)
        cv2.rectangle(image, tl, br, (0, 255, 0), 2)
        cv2.putText(image, text, (tl[0], tl[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    return image

def test():
    img = cv2.imread("Untitled.png")
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, (0, 0, 150), (255, 5, 255))
    cv2.imshow('mask before and with nzmask', mask)

    # Build mask of non black pixels.
    nzmask = cv2.inRange(hsv, (0, 0, 5), (255, 255, 255))

    # Erode the mask - all pixels around a black pixels should not be masked.
    nzmask = cv2.erode(nzmask, np.ones((3, 3)))
    cv2.imshow('nzmask', nzmask)

    mask = mask & nzmask

    new_img = img.copy()
    new_img[np.where(mask)] = 255

    cv2.imshow('mask', mask)
    cv2.imshow('new_img', new_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    pyautogui.confirm(
        text='Press OK to grab image on location({})'.format(
            lf.get(Locations.TRADE_WINDOW_OTHER)),
        title='Grab image',
        buttons=['OK'])

    # image = get_image(lf.get(Locations.TRADE_WINDOW_OTHER))
    image = cv2.imread("ocr.jpg")
    show_image(image)
    image_filtered = OCR.getFilteredImage(image)
    show_image(image_filtered)

    custom_config = r'-c tessedit_char_whitelist=0123456789 --oem 3 --psm 6 digits'
    d = pytesseract.image_to_data(image_filtered, config=custom_config,
                                  lang='poe',
                                  output_type=Output.DICT)
    print(d)
    for i in range(0, len(d['conf'])):
        print(d['conf'][i], d['text'][i])
    # n_boxes = len(d['text'])
    # for i in range(n_boxes):
    #     if int(d['conf'][i]) > 70:
    #         (x, y, w, h) = (
    #             d['left'][i], d['top'][i], d['width'][i], d['height'][i])
    #         image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    # show_image(image)
