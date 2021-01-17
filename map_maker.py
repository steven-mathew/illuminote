import imutils
from skimage import exposure
import numpy as np
import cv2
import utils
import block


class ImageWarper:

    def __init__(self, image_path, height, draw_filters=False):
        self.image = cv2.imread(image_path)
        self.height = height
        self.ratio = self.image.shape[0] / self.height
        self.resized_image = imutils.resize(self.image, height=self.height)
        # self.image_to_warp = cv2.imread(image_to_warp)
        # self.resized_image_to_warp = imutils.resize(
        # self.image_to_warp, height=self.height)

        self.gray, self.edges = self._preprocess()
        self.contours = self._grab_contours()
        self.screen_contour = self._get_screen_contour()
        self.warp()

        if draw_filters:
            self._draw_filters()

    def _preprocess(self):
        gray = cv2.cvtColor(self.resized_image, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 11, 17, 17)

        edges = cv2.Canny(gray, 30, 200)

        return gray, edges

    def _grab_contours(self):
        cnts = cv2.findContours(
            self.edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:10]

        return cnts

    def _get_screen_contour(self):
        for c in self.contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.015 * peri, True)

            if len(approx) == 4:
                return approx

        return None

    # See https://www.pyimagesearch.com/2014/05/05/building-pokedex-python-opencv-perspective-warping-step-5-6/

    def warp(self):
        points = self.screen_contour.reshape(4, 2)
        rect = np.zeros((4, 2), dtype="float32")

        s = points.sum(axis=1)
        rect[0] = points[np.argmin(s)]
        rect[2] = points[np.argmax(s)]

        diff = np.diff(points, axis=1)
        rect[1] = points[np.argmin(diff)]
        rect[3] = points[np.argmax(diff)]

        rect *= self.ratio

        (tl, tr, br, bl) = rect

        widthA = utils.distance(br, bl)
        widthB = utils.distance(tr, tl)
        heightA = utils.distance(tr, br)
        heightB = utils.distance(tl, bl)

        maxWidth = max(int(widthA), int(widthB))
        maxHeight = max(int(heightA), int(heightB))

        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")

        self.transformation_matrix = cv2.getPerspectiveTransform(rect, dst)
        self.warp = cv2.warpPerspective(
            self.image, self.transformation_matrix, (maxWidth, maxHeight))

        # self.warped_state = cv2.warpPerspective(
        # self.image_to_warp, self.transformation_matrix, (
        # maxWidthm, maxHeight)
        # )

    def _draw_filters(self):
        cv2.drawContours(self.resized_image, [
                         self.screen_contour], -1, (0, 255, 0), 3)
        cv2.imshow("Warped", imutils.resize(self.warp, height=self.height))
        cv2.imshow("Original", self.resized_image)
        cv2.imshow("Edge", self.edges)

        cv2.waitKey()

    def save_warped_image(self):
        cv2.imwrite('warp.png', imutils.resize(self.warp, height=self.height))
        # cv2.imwrite('warped_game.png', imutils.resize(
        # self.warp, height=self.height))


class BlockGrabber:
    def __init__(self, image_path, draw_filters=False):
        self.image = cv2.imread(image_path)
        self._preprocess()
        self.contour_list = self.grab_contours()

        if draw_filters:
            self._draw_filters()

    def _preprocess(self):
        self.hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        self.hue, self.saturation, self.value = cv2.split(self.hsv)
        _, self.thresholded = cv2.threshold(
            self.saturation, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        self.median_filtered = cv2.medianBlur(self.thresholded, 5)

        self.morphologically_transformed = cv2.erode(
            self.median_filtered, None, iterations=2)
        self.morphologically_transformed = cv2.dilate(
            self.median_filtered, None, iterations=2)

    def grab_contours(self):
        contours, _ = cv2.findContours(
            self.median_filtered, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        contour_list = []

        for c in contours:
            area = cv2.contourArea(c)
            x, y, w, h = cv2.boundingRect(c)
            rect_area = w*h
            extent = float(area) / rect_area

            if 0.8 < extent < 1 and area > 1000:
                mean_colour = np.array(
                    cv2.mean(self.image[y:y+h//2, x:x+w//2])).astype(np.uint8)
                mean_colour = mean_colour[::-1][1:]  # BGR to RGB
                # print(mean_colour)
                first = cv2.drawContours(self.image, [c], -1, (0, 255, 0), 2)
                second = cv2.circle(
                    self.image, (x, y), 1, (0, 0, 255), 5)
                contour_list.append((x, y, w, h, mean_colour))

        return contour_list

    def _draw_filters(self):
        cv2.imshow('Original', self.image)
        cv2.imshow('HSV Image', self.hsv)
        cv2.imshow('Saturation Image', self.saturation)
        cv2.imshow('Thresholded Image', self.thresholded)
        cv2.imshow('Median Filtered Image', self.median_filtered)

        cv2.waitKey()


# m = ImageWarper('12.jpg', 720, False)
# m.save_warped_image()

# b = BlockGrabber('warp.png', True)
