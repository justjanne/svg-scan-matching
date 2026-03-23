import os.path

import cv2
import numpy as np

expected_area = [0.5753084381815857, 0.5467924904648126, 0.45695676920198913, 0.4392252254528492, 0.4677225878383498, 0.49561579603381417, 0.44423693846760903, 0.43684253903088216, 0.4427445014371113, 0.45522605374243374, 0.42984222264958705, 0.43813925012606203, 0.4461545025303917, 0.4615909343475532, 0.4264104160571914, 0.4211077442579957, 0.5057132316066594, 0.459597952700799, 0.45305599680825287, 0.43751091314936774, 0.49572722503376854, 0.437577533138721, 0.45807031985809316]
expected_perimeter = [8.475059958984831, 7.814769698333799, 7.913946687534231, 7.871244502984462, 7.888532160571519, 7.772311509216155, 8.04347692764291, 8.02672984510532, 7.801743177509711, 7.894799054231928, 8.043351811370389, 7.886179744982448, 7.8947350636072695, 8.015197360076522, 7.897068980390494, 8.068480477519715, 7.724941956812329, 7.833536336135709, 7.818555238715287, 7.876754289693158, 7.835915021236471, 7.838778607100985, 7.899469446098373]
expected_hull_area = [2.1161309179050316, 2.104806760524752, 2.0988555232000397, 2.083789073763341, 2.076268981047089, 2.110364034724628, 2.1209283303018562, 2.1062408003159465, 2.1100835504031603, 2.0926935224721492, 2.093394733275819, 2.097872518472193, 2.1069807423327913, 2.097029942991181, 2.1293424488795734, 2.0983988816111383, 2.108961613117289, 2.0989986937941123, 2.0937659281067114, 2.083800371047535, 2.1053003110614905, 2.097872518472193, 2.1286293879831564]
expected_hull_perimeter = [5.680899340025476, 5.672100244956982, 5.694527523537542, 5.677312418292794, 5.656436470205475, 5.689753244339635, 5.708747080427075, 5.688826967935865, 5.689753244339635, 5.666075086460248, 5.679842283397696, 5.6836295374948405, 5.685579771949727, 5.683735916807797, 5.713643368666925, 5.6946388443890745, 5.6759926916789185, 5.677863639860343, 5.681491369178707, 5.684942428290507, 5.671817976658715, 5.6836295374948405, 5.713751344707583]
expected_radius = [60.208072662353516, 60.25165557861328, 59.67002487182617, 59.634403228759766, 60.208072662353516, 59.70981216430664, 59.211585998535156, 59.17145919799805, 59.70981216430664, 59.70981216430664, 59.70981216430664, 59.67002487182617, 59.753761291503906, 59.67002487182617, 59.211585998535156, 59.17329788208008, 59.70981216430664, 59.753761291503906, 59.61245346069336, 59.636253356933594, 59.753761291503906, 59.67002487182617, 59.211585998535156]

def calculate_params(values):
    min_val = min(values)
    max_val = max(values)
    std = (max_val + min_val) / 2
    dev = (max_val - min_val)
    return (std, dev)

params_area = calculate_params(expected_area)
params_perimeter = calculate_params(expected_perimeter)
params_hull_area = calculate_params(expected_hull_area)
params_hull_perimeter = calculate_params(expected_hull_perimeter)
params_radius = calculate_params(expected_radius)


def detect_registration_marks(file: str, debug_dir: str | None = None):
    im_scan = cv2.imread(file)
    im_scan = cv2.resize(im_scan, (3504, im_scan.shape[0] * 3504 // im_scan.shape[1]))

    write_debug_image(im_scan, file, "_scan", debug_dir)

    im_threshold = preprocess_image(im_scan)
    write_debug_image(im_threshold, file, "_threshold", debug_dir)

    contours, hierarchy = cv2.findContours(im_threshold, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    candidates = [c for c in contours if match_contour(c)]
    marks = [process_contour(c) for c in candidates]

    if debug_dir:
        im_contours = im_scan
        im_contours = cv2.drawContours(im_contours, candidates, -1, (0, 0, 255), 2)
        for candidate in candidates:
            rect = cv2.minAreaRect(candidate)
            box = cv2.boxPoints(rect)
            box = np.intp(box)
            im_contours = cv2.drawContours(im_contours, [box], -1, (255, 255, 0), 2)
        for mark in marks:
            im_contours = cv2.circle(im_contours, mark, 2, (0, 255, 0), 2)
            im_contours = cv2.circle(im_contours, mark, 60, (0, 255, 0), 2)
        write_debug_image(im_contours, file, "_contours", debug_dir)

    return [
        to_percent(im_scan, mark)
        for mark in marks
    ]

def to_percent(scan: cv2.typing.MatLike, point: (float, float)) -> (float, float):
    x, y = point
    height, width, _ = scan.shape
    return x * 1.0 / width, y * 1.0 / height


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

    im_preprocessed = cv2.bitwise_and(im_grayscale, im_threshold)
    return im_preprocessed


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

    match_area = match_value(area, params_area)
    match_perimeter = match_value(perimeter, params_perimeter)

    match_hull_area = match_value(hull_area, params_hull_area)
    match_hull_perimeter = match_value(hull_perimeter, params_hull_perimeter)
    match_radius = match_value(radius, params_radius)

    match = match_radius and match_hull_perimeter and match_perimeter and match_area and match_hull_area
    if match:
        print(f"area={area}, perimeter={perimeter}, hull_area={hull_area}, hull_perimeter={hull_perimeter}, radius={radius}")
    return match


def match_value(actual: float, params: (float, float)) -> bool:
    expected, deviation = params
    return abs(actual - expected) < (expected * deviation)
