import math
import sys
from typing import Sequence
from xml.dom.minidom import parse

import os
import cv2
import numpy

import detection

DEBUGPATH = os.getenv("FCM_DEBUG_PATH")

CORRECTION_DATA = [(111,114), (2354,110), (111,3362), (2355,3358)]
CORRECTION_WIDTH = 3504
CORRECTION_HEIGHT = 3529

MAT_WIDTH = 296.7
MAT_HEIGHT = 301

REGISTRATION_MARKS = [(10, 10), (200, 10), (10, 287), (200, 287)]

def apply_correction(point):
    x, y = point
    points = cv2.transform(
        numpy.array([numpy.array([numpy.array([x, y], dtype=numpy.float32)])]),
        CORRECTION,
    )
    x, y = points[0][0]
    return (float(x), float(y))

def distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt(math.pow(x1 - x2, 2) + math.pow(y2 - y1, 2))


def sort_marks(marks: list[(float, float)]) -> list[(float, float)]:
    min_x = min(x for (x, _) in marks)
    max_x = max(x for (x, _) in marks)
    min_y = min(y for (_, y) in marks)
    max_y = max(y for (_, y) in marks)
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    center = (center_x, center_y)

    distances = [distance(center, mark) for mark in marks]
    distances.sort()
    median_distance = distances[len(distances) // 2]

    marks.sort(key=lambda mark: abs(median_distance - distance((center_x, center_y), mark)))
    marks = marks[0:4]

    top_left = next((x, y) for (x, y) in marks if x < center_x and y < center_y)
    top_right = next((x, y) for (x, y) in marks if x > center_x and y < center_y)
    bottom_left = next((x, y) for (x, y) in marks if x < center_x and y > center_y)
    bottom_right = next((x, y) for (x, y) in marks if x > center_x and y > center_y)

    return [top_left, top_right, bottom_left, bottom_right]


def calculate_transform(
        marks: [(float, float), (float, float), (float, float), (float, float)],
) -> cv2.typing.MatLike:
    marks = [apply_correction(mark) for mark in marks]
    matrix, _ = cv2.estimateAffine2D(numpy.array(REGISTRATION_MARKS), numpy.array(marks), confidence=0.99999, maxIters=20000, refineIters=0)
    return matrix


def format_transform_matrix(matrix: cv2.typing.MatLike) -> str:
    return "matrix({0:.5f} {1:.5f} {3:.5f} {4:.5f} {2:.5f} {5:.5f})".format(
        float(matrix[0][0]), float(matrix[1][0]), float(matrix[0][2]),
        float(matrix[0][1]), float(matrix[1][1]), float(matrix[1][2]),
    )


def generate_cut(source: str, target: str, transform: cv2.typing.MatLike):
    dom = parse(source)
    document = dom.firstChild
    wrapper = dom.createElement("g")
    wrapper.setAttribute("transform", format_transform_matrix(transform))
    transformable = [node for node in document.childNodes if node.nodeName == "g"]
    for node in transformable:
        document.removeChild(node)
        wrapper.appendChild(node)
    document.appendChild(wrapper)
    with open(target, "w") as writer:
        dom.writexml(writer)


def process_cut(source: str, scan: str, out: str):
    marks = sort_marks(detection.detect_registration_marks(scan, DEBUGPATH))
    transform = calculate_transform(marks)
    generate_cut(source, out, transform)


def calculate_correction():
    marks = CORRECTION_DATA
    marks = [(x / CORRECTION_WIDTH, y / CORRECTION_HEIGHT) for (x, y) in marks]
    matrix, _ = cv2.estimateAffine2D(numpy.array(marks), numpy.array(REGISTRATION_MARKS), confidence=0.99999, maxIters=20000, refineIters=100)
    marks = [(x * MAT_WIDTH, y * MAT_HEIGHT) for (x, y) in marks]
    scaled_matrix, _ = cv2.estimateAffine2D(numpy.array(marks), numpy.array(REGISTRATION_MARKS), confidence=0.99999, maxIters=20000, refineIters=100)
    print("MAT CORRECTION", format_transform_matrix(scaled_matrix))
    return matrix

CORRECTION = calculate_correction()

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 3:
        process_cut(args[0], args[1], args[2])
