import os
import cv2
import numpy as np
import extcolors
from PIL import Image


class ImageProcessor:
    def __init__(self):
        pass

    def getMaskedWall(self, img, floodFillMask, seedPoint, color):
        # Floodfill
        output = img.copy()
        # self.seed = (156, 213)

        loDiff = (8, 8, 8, 8)
        upDiff = (8, 8, 8, 8)

        cv2.floodFill(
            output,
            floodFillMask,
            seedPoint=seedPoint,
            newVal=color,
            loDiff=loDiff,
            upDiff=upDiff,
        )
        # cv2.circle(output, self.seed, 2, self.wallColor, cv2.FILLED, cv2.LINE_AA);
        # cv2.imshow("floodFill", output)

        # Convert from cv image to rgb for display
        # output = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
        return output

    def getDetectedWalls(self, img, predictions, segmentInfo):
        # Get wall regions from predictions
        objectId = next(
            (sub for sub in segmentInfo if sub["category_id"] == 52), {"id": 0}
        )["id"]

        grayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        (thresh, binary_mask) = cv2.threshold(grayImage, 127, 255, cv2.THRESH_BINARY)

        xpx, ypx = img.shape[:2]
        for i in range(xpx):
            for j in range(ypx):
                if predictions[i][j] != objectId:
                    binary_mask[i][j] = 0
                else:
                    binary_mask[i][j] = 255

        # kernel = np.ones((2, 2), np.uint8)
        binary_mask = cv2.erode(binary_mask, None, iterations=5)

        mask = img.copy()
        for i in range(xpx):
            for j in range(ypx):
                if binary_mask[i][j] != 255:
                    mask[i][j] = (0, 0, 0)

        return mask

    def getWallColor(self, wallsDetected):
        wallRegion = cv2.cvtColor(wallsDetected, cv2.COLOR_BGR2RGB)
        wallRegion_pil = Image.fromarray(wallRegion)

        colors, pixel_count = extcolors.extract_from_image(wallRegion_pil)
        max_color = max(
            colors, key=lambda color: color[1] if color[0] != (0, 0, 0) else 0
        )
        # print(max_color)

        return max_color[0]

    def getColorMask(self, img, color):
        rgb_color = np.uint8([[color[::-1]]])
        hsv_color = cv2.cvtColor(rgb_color, cv2.COLOR_BGR2HSV)[0][0]
        # print(hsv_color)
        hue = hsv_color[0]
        sat = hsv_color[1]

        hue_diff = 1
        sat_diff = 80

        hsv_color[0] = (hue - hue_diff) if (hue - hue_diff) > 0 else 0
        hsv_color[1] = (sat - sat_diff) if (sat - sat_diff) > 0 else 0
        hsv_color[2] = 0
        lower_range = np.array(hsv_color)

        hsv_color[0] = (hue + hue_diff) if (hue + hue_diff) < 180 else 180
        hsv_color[1] = (sat + sat_diff) if (sat + sat_diff) < 180 else 180
        hsv_color[2] = 255
        upper_range = np.array(hsv_color)
        # print(lower_range, upper_range)

        color_mask = cv2.inRange(
            cv2.cvtColor(img, cv2.COLOR_BGR2HSV), lower_range, upper_range
        )

        return color_mask

    def getWallMask(self, img, colorMask, floodFillMask, color):
        loDiff = (5, 5, 5, 5)
        upDiff = (5, 5, 5, 5)

        # fill openings
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        color_mask = cv2.morphologyEx(colorMask, cv2.MORPH_OPEN, kernel)

        # fill closings
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, kernel)

        output = img.copy()
        xpx, ypx = img.shape[:2]

        for i in range(xpx):
            for j in range(ypx):
                if (
                    color_mask[i][j] == 255 and tuple(output[i][j]) != color
                ):  # and tuple(mask[i][j]) != (0, 0, 0) :
                    cv2.floodFill(
                        output,
                        floodFillMask,
                        seedPoint=(j, i),
                        newVal=color,
                        loDiff=loDiff,
                        upDiff=upDiff,
                    )

        return output

    def applyPaint(self, img, highlightedWall):
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        v_channel = hsv_img[:, :, 2]
        hsvMaskedWall = cv2.cvtColor(highlightedWall, cv2.COLOR_BGR2HSV)
        painted = hsvMaskedWall.copy()
        xpx, ypx, bitpx = painted.shape

        for i in range(xpx):
            for j in range(ypx):
                painted[i][j] = (painted[i][j][0], painted[i][j][1], v_channel[i][j])

        painted = cv2.cvtColor(painted, cv2.COLOR_HSV2BGR)

        # Convert from cv image to rgb for display
        # painted = cv2.cvtColor(painted, cv2.COLOR_BGR2RGB)

        return painted

    def getSeedPoint(self, detectedWall):
        wallRegion = cv2.cvtColor(detectedWall, cv2.COLOR_BGR2RGB)
        wallRegion_pil = Image.fromarray(wallRegion)

        colors, pixel_count = extcolors.extract_from_image(wallRegion_pil)
        max_color = max(
            colors, key=lambda color: color[1] if color[0] != (0, 0, 0) else 0
        )
        print(max_color)
        indices = np.where(wallRegion == [max_color[0]])
        coordinates = list(zip(indices[0], indices[1]))
        l = len(coordinates)
        seedPoint = (coordinates[0][1], coordinates[0][0])

        return seedPoint

    def getFloodfillMask(self, image):
        img = image.copy()
        # kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        # img = cv2.filter2D(src=img, ddepth=-1, kernel=kernel)

        # img = cv2.bilateralFilter(src=img, d=9, sigmaColor=75, sigmaSpace=75)

        # grayscale
        gs_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # hsv
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # cv2.imshow("hsv_img", hsv_img)
        (h_channel, s_channel, v_channel) = cv2.split(hsv_img)

        # edge in s_channel

        # Blur the image for better edge detection
        gs_blur = cv2.GaussianBlur(gs_img, (3, 3), sigmaX=0, sigmaY=0)

        # Blur the image for better edge detection
        s_blur = cv2.GaussianBlur(s_channel, (3, 3), sigmaX=0, sigmaY=0)

        high_thresh, thresh_im = cv2.threshold(
            gs_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        lowThresh = 0.5 * high_thresh

        # high_thresh = 255
        # lowThresh = 0
        # Canny Edge Detection img
        edges_gs = cv2.Canny(
            image=gs_blur, threshold1=lowThresh, threshold2=high_thresh
        )

        # Canny Edge Detection img
        edges_s = cv2.Canny(image=s_blur, threshold1=lowThresh, threshold2=high_thresh)

        # Merge edges

        edges = cv2.add(edges_gs, edges_s)

        # Dilation to extend
        # Taking a matrix of size 5 as the kernel
        kernel = np.ones((2, 2), np.uint8)

        # img_erosion = cv2.erode(sharpened_edges, kernel, iterations=1)
        edges_dilation = cv2.dilate(edges, kernel, iterations=2)

        mflood = img.copy()

        h, w = edges_dilation.shape[:2]
        img_mask = np.zeros((h + 2, w + 2), np.uint8)
        img_mask[1:-1, 1:-1] = edges

        return img_mask

    def getGradientedges(self, img):
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        gradient = cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel)

        high_cont_grad = cv2.convertScaleAbs(gradient, alpha=5, beta=0)
        kernel = np.ones((2, 2), np.uint8)
        erosion = cv2.erode(high_cont_grad, kernel, iterations=1)

        denoised = cv2.fastNlMeansDenoisingColored(erosion, None, 10, 10, 7, 21)
        edges = cv2.Canny(denoised, 13, 255)
        edges = cv2.dilate(edges, kernel, iterations=2)

        h, w = denoised.shape[:2]
        img_mask = np.zeros((h + 2, w + 2), np.uint8)
        img_mask[1:-1, 1:-1] = edges
        return img_mask
