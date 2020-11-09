import cv2 as cv
import numpy as np


class Vision:

    def get_click_points(self, rectangles):
        points = []

        for (x, y, w, h) in rectangles:
            center_x = x + int(w/2)
            center_y = y + int(h/2)
            points.append((center_x, center_y))

        return points

    def draw_rectangles(self, haystack_img, rectangles):
        line_color = (0, 255, 0)
        line_type = cv.LINE_4

        for (x, y, w, h) in rectangles:
            top_left = (x, y)
            bottom_right = (x + w, y + h)
            cv.rectangle(haystack_img, top_left, bottom_right, line_color, lineType=line_type)

        return haystack_img