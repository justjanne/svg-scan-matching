#!/usr/bin/env python3
import base64
import dataclasses
import json
import sys
import xml.dom.minidom
from base64 import b64encode

from contours import list_window, Contour
from draw_command import DrawCommandType
from fcm import PathDto, PointDto, OutlineBezierDto, SegmentBezierDto, OutlineLineDto, SegmentLineDto, \
    PathFlagsDto, PieceDto, PieceFlagsDto, FileDto, CutDataDto, ThumbnailDto
from path import Path
from svg import find_elements


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, bytes):
            return b64encode(o).decode()
        return super().default(o)


def point_to_fcm(x: float, y: float) -> PointDto:
    return PointDto(int(x * 100), int(y * 100))


def path_to_fcm(path: Path) -> list[PathDto]:
    paths = []
    outlines = []
    start: PointDto | None = None

    for command in path.commands:
        if command.type == DrawCommandType.BEZIER:
            segments = [SegmentBezierDto(
                point_to_fcm(c1x, c1y), point_to_fcm(c2x, c2y), point_to_fcm(x, y)
            ) for (c1x, c1y, c2x, c2y, x, y) in list_window(command.arguments, 6)]
            if len(segments) > 0:
                outlines.append(OutlineBezierDto(segments))
        if command.type == DrawCommandType.LINE:
            segments = [SegmentLineDto(point_to_fcm(x, y)) for (x, y) in list_window(command.arguments, 2)]
            if len(segments) > 0:
                outlines.append(OutlineLineDto(segments))
        if command.type == DrawCommandType.MOVE:
            if len(outlines) != 0 and start is not None:
                paths.append(PathDto(PathFlagsDto(open=True), start, outlines))
            start = point_to_fcm(command.arguments[0], command.arguments[1])
            outlines = []
            segments = [SegmentLineDto(point_to_fcm(x, y)) for (x, y) in list_window(command.arguments[2:], 2)]
            if len(segments) > 0:
                outlines.append(OutlineLineDto(segments))
        if command.type == DrawCommandType.CLOSE:
            if len(outlines) != 0 and start is not None:
                paths.append(PathDto(PathFlagsDto(open=False), start, outlines))
            start = None
            outlines = []
    if len(outlines) != 0 and start is not None:
        paths.append(PathDto(PathFlagsDto(open=True), start, outlines))
    return paths


def piece_to_fcm(piece: xml.dom.minidom.Node, label: str = "") -> PieceDto:
    paths = find_elements(piece, tag_name="path")
    paths = [Path.of(path.getAttribute("d")) for path in paths]
    contours = [contour for path in paths for contour in Contour.of(path)]
    min_x = min(contour.min_x() for contour in contours)
    min_y = min(contour.min_y() for contour in contours)
    max_y = max(contour.max_y() for contour in contours)
    max_x = max(contour.max_x() for contour in contours)
    paths = [fcm_path for path in paths for fcm_path in path_to_fcm(path)]
    size = point_to_fcm(max_x - min_x, max_y - min_y)
    return PieceDto(size.x, size.y, 0, 0, (1.0, 0.0, 0.0, 1.0, 0.0, 0.0), PieceFlagsDto(), label, paths)


def extract_paths(filename: str) -> FileDto:
    dom = xml.dom.minidom.parse(filename)
    return FileDto(
        content_id=400000000,
        short_name="",
        long_name="",
        author_name="",
        copyright="",
        cut_data=CutDataDto(
            mat_id=0,
            cut_width=29667,
            cut_height=29880,
            seam_allowance_width=2000,
        ),
        thumbnail=ThumbnailDto(
            block_width=3,
            block_height=3,
            data=base64.decodebytes(
                b"Qk1eBAAAAAAAAD4AAAAoAAAAWAAAAFgAAAABAAEAAAAAAAAAAAAlFgAAJRYAAAIAAAACAAAAAAAA/////////////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wD//////////////wA=")
        ),
        pieces=[
            piece_to_fcm(dom, "A01"),
        ],
    )


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 2:
        converted = extract_paths(args[0])
        with open(args[1], "w") as out:
            json.dump(converted, out, cls=CustomJsonEncoder)
