import os

from detect.detection import detect_registration_marks


def test_detect_registration_marks():
    test_dir = "tests/resources/scan"
    files = sorted(os.listdir(test_dir))
    for file in files:
        detect_registration_marks(os.path.join(test_dir, file), "build/test")
