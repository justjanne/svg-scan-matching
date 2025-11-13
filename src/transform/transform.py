import dataclasses
from typing import Optional

from svgelements import SVGElement, SVG, Path, Shape, Group, Move, Line, CubicBezier, QuadraticBezier, Arc, Close

ATTR_GROUP_MODE = "{http://www.inkscape.org/namespaces/inkscape}groupmode"
ATTR_LABEL = "{http://www.inkscape.org/namespaces/inkscape}label"
ATTR_VISIBILITY = "visibility"


@dataclasses.dataclass
class CutFile:
    registration_marks: list[tuple[float, float]]
    layers: dict[str, list[Path]]


def transform_file(file: SVG) -> Optional[CutFile]:
    registration = file.get_element_by_id("registration")
    if not isinstance(registration, Group):
        return None
    registration_marks = transform_registration_marks(registration)
    layers = {}
    for element in file:
        if isinstance(element, Group):
            group = transform_group(element)
            if group is not None:
                layers[element.id] = group
    return CutFile(registration_marks, layers)


def transform_registration_marks(group: Group) -> list[tuple[float, float]]:
    registration_marks = []
    for element in group.select():
        if isinstance(element, Path):
            (x1, y1, x2, y2) = element.bbox()
            x = round((x1 + x2) / 2, 2)
            y = round((y1 + y2) / 2, 2)
            registration_marks.append((x, y))
    return registration_marks


def transform_group(group: Group) -> Optional[list[Path]]:
    if group.id.startswith("cut"):
        elements = []
        for element in group.select():
            processed_element = transform_element(element)
            if processed_element is not None:
                elements.append(processed_element)
        if elements:
            return elements
    return None


def transform_element(element: SVGElement) -> Optional[Path]:
    if ATTR_VISIBILITY in element.values and element.values[ATTR_VISIBILITY] == "hidden":
        return None
    if isinstance(element, Path):
        output = Path(element.d(relative=False))
        output.reify()
        if len(output) != 0:
            return output
    elif isinstance(element, Shape):
        output = Path(element.d(relative=False))
        output.reify()
        if len(output) != 0:
            return output
    return None


def transform_path(path: Path) -> list[Path]:
    paths: list[Path] = []
    outline = Path()
    for segment in path:
        if isinstance(segment, Move):
            if len(outline) != 0:
                paths.append(outline)
                outline = Path()
            outline.append(Move(
                start=segment.start,
                end=segment.end,
            ))
        elif isinstance(segment, Line):
            outline.append(Line(
                start=segment.start,
                end=segment.end,
            ))
        elif isinstance(segment, CubicBezier):
            outline.append(CubicBezier(
                start=segment.start,
                control1=segment.control1,
                control2=segment.control2,
                end=segment.end,
                smooth=False,
            ))
        elif isinstance(segment, QuadraticBezier):
            outline.append(CubicBezier(
                start=segment.start,
                control1=segment.start + (segment.control - segment.start) * (2 / 3),
                control2=segment.end + (segment.end - segment.control) * (2 / 3),
                end=segment.end,
                smooth=False,
            ))
        elif isinstance(segment, Arc):
            for subsegment in segment.as_cubic_curves():
                outline.append(CubicBezier(
                    start=subsegment.start,
                    control1=subsegment.control1,
                    control2=subsegment.control2,
                    end=subsegment.end,
                    smooth=False,
                ))
        elif isinstance(segment, Close):
            if len(outline) != 0:
                paths.append(outline)
                outline = Path()
        else:
            print("Unknown segment:", segment)
    if len(outline) != 0:
        paths.append(outline)
    return paths
