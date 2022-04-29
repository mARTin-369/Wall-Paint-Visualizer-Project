from Detector import *
import cv2
import numpy as np

from image_processor import ImageProcessor

# Model = WallDetector()
detector = Detector("PS")
imageProcessor = ImageProcessor()

imgPath = r"D:\Martin\beproj\Wall_Paint_Visualizer\GUI\images\room1.jpg"
predictions, segmentInfo = detector.onImage(imgPath)
img = cv2.imread(imgPath)
# img = cv2.resize(img, (0, 0), fx=0.8, fy=0.8)

wallsDetected = imageProcessor.getDetectedWalls(img, predictions, segmentInfo)
cv2.imshow("wallsDetected", wallsDetected)

wallColor = imageProcessor.getWallColor(wallsDetected)

floodFillMask = imageProcessor.getFloodfillMask(img)
cv2.imshow("floodFillMask", floodFillMask)

colorMask = imageProcessor.getColorMask(wallsDetected, wallColor)
cv2.imshow("colorMask", colorMask)

result = imageProcessor.getWallMask(img, colorMask, floodFillMask, (8, 255, 8))
cv2.imshow("result", result)

grayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

xpx, ypx = img.shape[:2]
for i in range(xpx):
    for j in range(ypx):
        if tuple(result[i][j]) == (8, 255, 8):
            grayImage[i][j] = 255
        else:
            grayImage[i][j] = 0

cv2.imshow("result", grayImage)

wallPath = ""
img = cv2.imread(wallPath)
tile = np.tile(img, (2, 3, 1))


cv2.waitKey(0)
cv2.destroyAllWindows()
