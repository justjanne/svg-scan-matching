import os

from scanalign.transform.parse import parse_svg
from scanalign.transform.util import patch_viewbox

patch_viewbox()

def test_detect_registration_marks():
    test_dir = "tests/resources/svg"
    files = sorted(os.listdir(test_dir))
    for file in files:
        parse_svg(os.path.join(test_dir, file), "build/test")
