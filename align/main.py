import math
import sys
from typing import Sequence
from xml.dom.minidom import parse

import cv2
import numpy

DEBUGPATH = os.getenv("FCM_DEBUG_PATH")

def close_enough(a, b):
    return min(a, b) / max(a, b) > 0.7


def find_contours(image: cv2.typing.MatLike) -> Sequence[cv2.typing.MatLike]:
    image_grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_grayscale = cv2.bitwise_not(image_grayscale)
    ret, thresh = cv2.threshold(image_grayscale, 60, 255, 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def prefilter_double(shape: numpy.shape, contour: cv2.typing.MatLike) -> bool:
    area = cv2.contourArea(contour)
    _, _, w, h = cv2.boundingRect(contour)
    contour_length = cv2.arcLength(contour, True)
    if 0 in [w, h, area, contour_length]:
        return False
    if not close_enough(contour_length, w * 2.2 + h * 2.2):
        return False
    if not close_enough(w, h):
        return False
    if not close_enough(area, w * 11):
        return False
    if not close_enough(w, shape[1] / 30):
        return False
    return True


def prefilter_single(shape: numpy.shape, contour: cv2.typing.MatLike) -> bool:
    area = cv2.contourArea(contour)
    _, _, w, h = cv2.boundingRect(contour)
    contour_length = cv2.arcLength(contour, True)
    if 0 in [w, h, area, contour_length]:
        return False
    if not close_enough(contour_length, w * 2.2 + h * 2.2):
        return False
    if not close_enough(w, h):
        return False
    if not close_enough(area, w * 11):
        return False
    if not close_enough(w, shape[1] / 60):
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


def merge_cluster(cluster: Sequence[numpy.array]) -> numpy.array:
    for el1 in cluster:
        for el2 in cluster:
            if numpy.array_equal(el1, el2):
                continue
            match = marks_match(el1, el2)
            if match is None:
                continue
            return cv2.boxPoints(cv2.minAreaRect(numpy.array(el1 + el2)))
    return None


def merge_clusters(candidates: list[list[(float, float)]]):
    xs = [point[0] for el in candidates for point in el]
    ys = [point[1] for el in candidates for point in el]
    if len(xs) == 0 or len(ys) == 0:
        return []

    min_x = min(xs)
    max_x = max(xs)
    min_y = min(ys)
    max_y = max(ys)
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
        merge_cluster(top_left),
        merge_cluster(top_right),
        merge_cluster(bottom_left),
        merge_cluster(bottom_right),
    ]

    return [mark for mark in marks if mark is not None]

def distance_mark(center: (float, float), mark: ((float, float), (float, float))):
    ((x1, x2), (y1, y2)) = mark
    distances = [
        distance((x1, y1), center),
        distance((x2, y1), center),
        distance((x1, y2), center),
        distance((x2, y2), center),
    ]
    return sum(distances) / len(distances)


def sort_marks(marks: list[list[(float, float)]]) -> list[((float, float), (float, float))]:
    min_x = min(x1 for ((x1, _), (_, _)) in marks)
    max_x = max(x2 for ((_, x2), (_, _)) in marks)
    min_y = min(y1 for ((_, _), (y1, _)) in marks)
    max_y = max(y2 for ((_, _), (_, y2)) in marks)
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    center = (center_x, center_y)

    distances = [distance_mark(center, mark) for mark in marks]
    distances.sort()
    median_distance = distances[len(distances) // 2]

    marks.sort(key=lambda mark: abs(median_distance - distance_mark((center_x, center_y), mark)))
    marks = marks[0:4]

    top_left = next(((x1, x2), (y1, y2)) for ((x1, x2), (y1, y2)) in marks if x2 < center_x and y2 < center_y)
    top_right = next(((x1, x2), (y1, y2)) for ((x1, x2), (y1, y2)) in marks if x1 > center_x and y2 < center_y)
    bottom_left = next(((x1, x2), (y1, y2)) for ((x1, x2), (y1, y2)) in marks if x2 < center_x and y1 > center_y)
    bottom_right = next(((x1, x2), (y1, y2)) for ((x1, x2), (y1, y2)) in marks if x1 > center_x and y1 > center_y)

    return [top_left, top_right, bottom_left, bottom_right]


def process_candidates(candidates: list[list[(float, float)]]) -> list[(float, float)]:
    return [
        (find_center(cnt, 0), find_center(cnt, 1))
        for cnt in candidates
    ]


def to_mm(shape: numpy.shape, point: (float, float)) -> (float, float):
    x, y = point
    height, width, _ = shape
    return x / width, y / height


def avg(*items: list[float]) -> float:
    if len(items) == 0:
        return 0.0
    return sum(items) / len(items)


def simplify_single(contour: numpy.array) -> numpy.array:
    _, points = cv2.minEnclosingTriangle(contour)
    return [(point[0][0], point[0][1]) for point in points]


def simplify_double(contour: numpy.array) -> numpy.array:
    rect = cv2.minAreaRect(contour)
    points = cv2.boxPoints(rect)
    return points


def add_border(image: cv2.typing.MatLike):
    for y in range(0, image.shape[0]):
        image[y, 0] = (255, 255, 255)
    for x in range(0, image.shape[1]):
        image[0, x] = (255, 255, 255)
    for y in range(0, image.shape[0]):
        image[y, image.shape[1] - 1] = (255, 255, 255)
    for x in range(0, image.shape[1]):
        image[image.shape[0] - 1, x] = (255, 255, 255)


def find_marks(file: str) -> [(float, float), (float, float), (float, float), (float, float)]:
    scan = cv2.imread(file)
    if DEBUGPATH != "":
        dbgScan = cv2.cvtColor(scan, cv2.COLOR_BGR2GRAY)
        dbgScan = cv2.cvtColor(dbgScan, cv2.COLOR_GRAY2RGB)

    add_border(scan)
    candidates = find_contours(scan)
    contours_single = [cnt for cnt in candidates if prefilter_single(scan.shape, cnt)]
    contours_double = [cnt for cnt in candidates if prefilter_double(scan.shape, cnt)]
    shapes_single = [simplify_single(cnt) for cnt in contours_single]
    shapes_double = [simplify_double(cnt) for cnt in contours_double]

    if DEBUGPATH is not None:
        dbg = dbgScan.copy()
        cv2.drawContours(dbg, contours_single, -1, (0, 0, 255), 2)
        cv2.drawContours(dbg, contours_double, -1, (255, 0, 0), 2)
        for tri in shapes_single:
            cv2.drawContours(dbg, [numpy.intp(tri)], -1, (0, 255, 255), 2)
        for rect in shapes_double:
            cv2.drawContours(dbg, [numpy.intp(rect)], -1, (0, 255, 255), 2)
        cv2.imwrite(DEBUGPATH+"/contours_1.jpg", dbg)

    marks = process_candidates(shapes_double + merge_clusters(shapes_single))

    if DEBUGPATH is not None:
        dbg = dbgScan.copy()
        for ((x1, x2), (y1, y2)) in marks:
            cv2.rectangle(dbg, numpy.intp((x1, y1)), numpy.intp((x2, y2)), (0, 255, 0), 2)
        cv2.imwrite(DEBUGPATH+"/contours_2.jpg", dbg)

    marks = sort_marks(marks)

    if DEBUGPATH is not None:
        dbg = dbgScan.copy()
        for ((x1, x2), (y1, y2)) in marks:
            cv2.rectangle(dbg, numpy.intp((x1, y1)), numpy.intp((x2, y2)), (0, 255, 0), 2)
        cv2.imwrite(DEBUGPATH + "/contours_3.jpg", dbg)

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
    marks = find_marks(scan)
    transform = calculate_transform(marks)
    generate_cut(source, out, transform)


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 3:
        process_cut(args[0], args[1], args[2])
