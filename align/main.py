import math
import sys
from typing import Sequence
from xml.dom.minidom import parse

import os
import cv2
import numpy

import detection

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


def apply_matrix(
        value: (float, float),
        matrix: (float, float, float, float, float, float)
) -> (float, float):
    x, y = value
    a, c, e, b, d, f = matrix
    return a * x + c * y + e, b * x + d * y + f


def calculate_transform(
        marks: [(float, float), (float, float), (float, float), (float, float)],
) -> (float, float, float, float, float, float):
    marks = [(x * 296.7, y * 301) for (x, y) in marks]
    target = [(10, 10), (200, 10), (10, 287), (200, 287)]
    matrix, _ = cv2.estimateAffine2D(numpy.array(target), numpy.array(marks))
    return (matrix[0][0], matrix[1][0], matrix[0][2]+0.5,
            matrix[0][1], matrix[1][1], matrix[1][2]+0.5)


def format_transform_matrix(matrix: (float, float, float, float, float, float)) -> str:
    return "matrix({0:.3f} {1:.3f} {3:.3f} {4:.3f} {2:.3f} {5:.3f})".format(
        matrix[0], matrix[1], matrix[2], matrix[3], matrix[4], matrix[5]
    )


def generate_cut(source: str, target: str, transform: (float, float, float, float, float, float)):
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
        dom.writexml(writer, indent="  ", addindent="  ", newl="\n")


def process_cut(source: str, scan: str, out: str):
    marks = sort_marks(detection.detect_registration_marks(scan))
    transform = calculate_transform(marks)
    generate_cut(source, out, transform)


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 3:
        process_cut(args[0], args[1], args[2])
