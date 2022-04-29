from os import listdir
from Detector import *
from random import seed
from PIL import ImageColor
from colorharmonies import *
from color_generator import *
import os
import time
import cv2
import uuid

# Model
# from Wall_Detection_Model.wallDetector import WallDetector
from image_processor import ImageProcessor

# Model = WallDetector()
detector = Detector("PS")
img_folder = "./images"
imageProcessor = ImageProcessor()

images = listdir(img_folder + "/inputs")
# print(images)

highlightColor = (8, 255, 8)

process_time = {
    "wall detection": [],
    "wall color extraction": [],
    "edge detection": [],
    "thresholding": [],
    "floodfill": [],
    "lumination": [],
}

accuracy = []

# Confusion matrix
def check_accuracy(result, expected):
    xpx, ypx = result.shape[:2]
    tp = tn = fp = fn = 0

    for i in range(xpx):
        for j in range(ypx):
            if expected[i][j] == highlightColor:
                if result[i][j] == highlightColor:
                    tp += 1
                else:
                    fn += 1
            elif result[i][j] == highlightColor:
                fp += 1
            else:
                tn += 1

    accuracy = (tp + tn) / (tp + tn + fp + fn)


for i, image in enumerate(images):
    print(f"started {i + 1}.", end="")

    input_file = f"{img_folder}/inputs/{image}"
    output_file = f"{img_folder}/outputs/{image}"

    start = time.time() * 1000
    predictions, segmentInfo = detector.onImage(input_file)
    img = cv2.imread(input_file)

    wallsDetected = imageProcessor.getDetectedWalls(img, predictions, segmentInfo)
    process_time["wall detection"].append(time.time() * 1000 - start)
    print(".", end="")
    # cv2.imshow("wallsDetected", wallsDetected)

    start = time.time() * 1000
    wallColor = imageProcessor.getWallColor(wallsDetected)
    process_time["wall color extraction"].append(time.time() * 1000 - start)
    print(".", end="")

    start = time.time() * 1000
    floodFillMask = imageProcessor.getFloodfillMask(img)
    process_time["edge detection"].append(time.time() * 1000 - start)
    print(".", end="")
    # cv2.imshow("floodFillMask", floodFillMask)

    start = time.time() * 1000
    colorMask = imageProcessor.getColorMask(wallsDetected, wallColor)
    process_time["thresholding"].append(time.time() * 1000 - start)
    print(".", end="")
    # cv2.imshow("colorMask", colorMask)

    start = time.time() * 1000
    highlightedWall = imageProcessor.getWallMask(
        img, colorMask, floodFillMask, highlightColor
    )
    process_time["floodfill"].append(time.time() * 1000 - start)
    print(".", end="")
    # cv2.imshow("highlightedWall", highlightedWall)

    start = time.time() * 1000
    paintedWall = imageProcessor.applyPaint(img, highlightedWall)
    process_time["lumination"].append(time.time() * 1000 - start)
    print(".")
    # cv2.imshow("paintedWall", paintedWall)

    cv2.waitKey(0)  # waits until a key is pressed
    cv2.destroyAllWindows()

    # Accuracy
    # expected_output = cv2.imread(output_file)
    # accuracy.append(check_accuracy(highlightedWall, expected_output))

    cv2.imwrite(output_file, highlightedWall)
    # if i == 4:
    #     break

    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

print("done..")

print(process_time)

for process, time_arr in process_time.items():
    print(f"{process}: {sum(time_arr)//len(time_arr)}")

# print(f"Accuracy: {sum(accuracy)//len(accuracy)}")
