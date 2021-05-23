import cv2
import cv2
import numpy as np
import imutils

image = cv2.imread('test.jpg')
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
lower_range = np.array([110,50,50])
upper_range = np.array([130,255,255])
mask = cv2.inRange(hsv, lower_range, upper_range)

# cv2.imshow('x', mask)

# gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
thresh = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

cv2.imshow('thresh', thresh)

close_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, close_kernel, iterations=3)

cv2.imshow('close', close)

# dilate_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (6, 6))
# dilate = cv2.dilate(close, dilate_kernel, iterations=1)

cv2.imshow('dilate', close)

cnts = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]
for c in cnts:
    area = cv2.contourArea(c)
    if area > 800 and area < 15000:
        x,y,w,h = cv2.boundingRect(c)
        cv2.rectangle(image, (x, y), (x + w, y + h), (100, 100, 255), -1)

cv2.imshow('image', image)
cv2.waitKey()
