import math
import sys
from typing import Sequence
from xml.dom.minidom import parse

import cv2 as cv
import numpy


def close_enough(a, b):
    return min(a, b) / max(a, b) > 0.7


def find_contours(image: cv.typing.MatLike) -> Sequence[cv.typing.MatLike]:
    image_grayscale = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    ret, thresh = cv.threshold(image_grayscale, 50, 255, 0)
    contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    return contours


def prefilter(shape: numpy.shape, contour: cv.typing.MatLike) -> bool:
    area = cv.contourArea(contour)
    _, _, w, h = cv.boundingRect(contour)
    contour_length = cv.arcLength(contour, True)
    if 0 in [w, h, area, contour_length]:
        return False
    if not close_enough(w, h):
        return False
    if not close_enough(w * h, 6.5 * area):
        return False
    if not close_enough(contour_length, w * 2 + 2 * h):
        return False
    if not close_enough(w, shape[1] / 55):
        return False
    return True


def distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt(math.pow(x1 - x2, 2) + math.pow(y2 - y1, 2))


def marks_match(mark1, mark2):
    for point1 in mark1:
        for point2 in mark2:
            if distance(point1, point2) < 5:
                return [point1, point2]
    return None


def find_center(points, index):
    return sorted(point[index] for point in points)[1:3]


def process_cluster(cluster):
    for el1 in cluster:
        for el2 in cluster:
            if numpy.array_equal(el1, el2):
                continue
            match = marks_match(el1, el2)
            if match is None:
                continue
            bounds = cv.boxPoints(cv.minAreaRect(numpy.array(el1 + el2)))
            return find_center(bounds, 0), find_center(bounds, 1)

    return None


def process_candidates(candidates: list[list[(float, float)]]):
    min_x = min(point[0] for el in candidates for point in el)
    max_x = max(point[0] for el in candidates for point in el)
    min_y = min(point[1] for el in candidates for point in el)
    max_y = max(point[1] for el in candidates for point in el)
    threshold_x = (min_x + max_x) / 2
    threshold_y = (min_y + max_y) / 2

    top_left = [el for el in candidates
                if all(point[0] < threshold_x for point in el)
                and all(point[1] < threshold_y for point in el)]
    top_right = [el for el in candidates
                 if all(point[0] > threshold_x for point in el)
                 and all(point[1] < threshold_y for point in el)]
    bottom_left = [el for el in candidates
                   if all(point[0] < threshold_x for point in el)
                   and all(point[1] > threshold_y for point in el)]
    bottom_right = [el for el in candidates
                    if all(point[0] > threshold_x for point in el)
                    and all(point[1] > threshold_y for point in el)]

    marks = [
        process_cluster(top_left),
        process_cluster(top_right),
        process_cluster(bottom_left),
        process_cluster(bottom_right),
    ]
    if None in marks:
        return []

    return marks


def to_mm(shape: numpy.shape, point: (float, float)) -> (float, float):
    x, y = point
    height, width, _ = shape
    return x / width, y / height


def avg(*items: list[float]) -> float:
    if len(items) == 0:
        return 0.0
    return sum(items) / len(items)


def simplify_shape(contour: numpy.array) -> numpy.array:
    _, points = cv.minEnclosingTriangle(contour)
    return [(point[0][0], point[0][1]) for point in points]


def find_marks(file: str) -> [(float, float), (float, float), (float, float), (float, float)]:
    scan = cv.imread(file)
    candidates = [simplify_shape(cnt) for cnt in find_contours(scan) if prefilter(scan.shape, cnt)]
    marks = process_candidates(candidates)

    return [
        to_mm(scan.shape, (avg(x1, x2), avg(y1, y2)))
        for ((x1, x2), (y1, y2)) in marks
    ]


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
    target = [(10, 9), (200, 9), (10, 287.7), (200, 287.7)]
    matrix, _ = cv.estimateAffine2D(numpy.array(target), numpy.array(marks))
    return (matrix[0][0], matrix[1][0], matrix[0][2],
            matrix[0][1], matrix[1][1], matrix[1][2])


def format_transform_matrix(matrix: (float, float, float, float, float, float)) -> str:
    return "matrix({0:.3f} {1:.3f} {3:.3f} {4:.3f} {2:.3f} {5:.3f})".format(
        matrix[0], matrix[1], matrix[2], matrix[3], matrix[4], matrix[5]
    )


def generate_cut(image: str, source: str, target: str, transform: (float, float, float, float, float, float)):
    dom = parse(source)
    document = dom.firstChild
    wrapper = dom.createElement("g")
    wrapper.setAttribute("transform", format_transform_matrix(transform))
    removable = [node for node in document.childNodes if node.tagName == "g"]
    for node in removable:
        document.removeChild(node)
        wrapper.appendChild(node)
    scan = dom.createElement("image")
    scan.setAttribute("href", image)
    scan.setAttribute("x", "0")
    scan.setAttribute("y", "0")
    scan.setAttribute("width", "296.7")
    scan.setAttribute("height", "301")
    document.appendChild(scan)
    document.appendChild(wrapper)
    with open(target, "w") as writer:
        dom.writexml(writer, indent="  ", addindent="  ", newl="\n")


def process_cut(source: str, scan: str):
    marks = find_marks(scan)
    transform = calculate_transform(marks)
    generate_cut(scan, source, source.replace(".svg", "_cut.svg"), transform)


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 2:
        process_cut(args[0], args[1])
