import os.path

import cv2


def detect_registration_marks(file: str, debug_dir: str | None = None):
    im_scan = cv2.imread(file)
    im_scan = cv2.resize(im_scan, (3504, im_scan.shape[0] * 3504 // im_scan.shape[1]))

    write_debug_image(im_scan, file, "_scan", debug_dir)

    im_threshold = preprocess_image(im_scan)
    write_debug_image(im_threshold, file, "_threshold", debug_dir)

    contours, hierarchy = cv2.findContours(im_threshold, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    candidates = [c for c in contours if match_contour(c)]
    marks = [process_contour(c) for c in candidates]

    if debug_dir is not None:
        im_contours = im_scan
        im_contours = cv2.drawContours(im_contours, contours, -1, (255, 0, 0), 3)
        im_contours = cv2.drawContours(im_contours, candidates, -1, (0, 0, 255), 3)
        for mark in marks:
            im_contours = cv2.circle(im_contours, mark, 2, (0, 255, 0), 2)
            im_contours = cv2.circle(im_contours, mark, 60, (0, 255, 0), 2)
        write_debug_image(im_contours, file, "_contours", debug_dir)


def preprocess_image(im_scan: cv2.typing.MatLike) -> cv2.typing.MatLike:
    im_hsl = cv2.cvtColor(im_scan, cv2.COLOR_BGR2HSV)
    im_saturation = im_hsl[:, :, 1]
    _, im_saturation = cv2.threshold(im_saturation, 60, 255, cv2.THRESH_BINARY)
    kernel_saturation = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    im_saturation = cv2.morphologyEx(im_saturation, cv2.MORPH_ERODE, kernel_saturation, iterations=2)
    im_saturation = cv2.morphologyEx(im_saturation, cv2.MORPH_DILATE, kernel_saturation, iterations=3)

    im_grayscale = cv2.cvtColor(im_scan, cv2.COLOR_BGR2GRAY)
    im_grayscale = cv2.bitwise_not(im_grayscale)

    kernel_denoise = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    _, im_denoise = cv2.threshold(im_grayscale, 63, 255, cv2.THRESH_BINARY)
    im_denoise = cv2.morphologyEx(im_denoise, cv2.MORPH_OPEN, kernel_denoise)

    im_grayscale = cv2.bitwise_and(im_grayscale, im_denoise)
    im_grayscale = cv2.bitwise_and(im_grayscale, cv2.bitwise_not(im_saturation))

    _, im_threshold = cv2.threshold(im_grayscale, 127, 255, cv2.THRESH_BINARY)
    im_threshold = cv2.morphologyEx(im_threshold, cv2.MORPH_DILATE, kernel_denoise, iterations=3)
    return im_threshold


def process_contour(contour: cv2.typing.MatLike) -> cv2.typing.Point:
    center, size, angle = cv2.minAreaRect(contour)
    center_x, center_y = center
    return [int(center_x), int(center_y)]


def write_debug_image(image: cv2.typing.MatLike, file: str, suffix: str, debug_dir: str | None):
    if debug_dir is not None:
        os.makedirs(debug_dir, exist_ok=True)
        basename, extension = os.path.splitext(os.path.basename(file))
        cv2.imwrite(os.path.join(debug_dir, f"{basename}{suffix}{extension}"), image)


def match_contour(contour: cv2.typing.MatLike) -> bool:
    _, radius = cv2.minEnclosingCircle(contour)

    area = cv2.contourArea(contour) / radius / radius
    perimeter = cv2.arcLength(contour, True) / radius

    hull = cv2.convexHull(contour)
    hull_area = cv2.contourArea(hull) / radius / radius
    hull_perimeter = cv2.arcLength(hull, True) / radius

    match_area = match_value(area, 1.0, .16)
    match_hull_area = match_value(hull_area, 2.26, .08)
    match_perimeter = match_value(perimeter, 7.78, .06)
    match_hull_perimeter = match_value(hull_perimeter, 5.78, .05)
    match_radius = match_value(radius, 64, 0.1)

    return match_radius and match_hull_perimeter and match_perimeter and match_area and match_hull_area


def match_value(actual: float, expected: float, deviation: float) -> bool:
    return abs(actual - expected) < (expected * deviation)
