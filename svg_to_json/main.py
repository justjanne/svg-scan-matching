#!/usr/bin/env python3
import base64
import dataclasses
import json
import math
import sys
import xml.dom.minidom
from base64 import b64encode

from contours import list_window, Contour
from draw_command import DrawCommandType
from fcm import PathDto, PointDto, OutlineBezierDto, SegmentBezierDto, OutlineLineDto, SegmentLineDto, \
    PathFlagsDto, PieceDto, PieceFlagsDto, FileDto, CutDataDto, ThumbnailDto, OutlineTypeDto
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
    return PointDto(int(round(x * 100)), int(round(y * 100)))


def path_to_fcm(path: Path, offset: PointDto = PointDto(0, 0)) -> list[PathDto]:
    paths = []
    outlines = []
    start: PointDto | None = None

    for i in range(0, len(path.commands)):
        command = path.commands[i]
        if command.type == DrawCommandType.QUADRATIC:
            if len(outlines) == 0:
                last = start
            else:
                last = outlines[-1].segments[-1].end
            segments = []
            for (c1x, c1y, c2x, c2y, x, y) in list_window(command.arguments, 6):
                control1 = point_to_fcm(c1x, c1y) - offset
                control2 = point_to_fcm(c2x, c2y) - offset
                end = point_to_fcm(x, y) - offset
                segments.append(SegmentBezierDto(
                    last + (control1 - last) * (2/3),
                    control2 + (control2 - control1) * (2/3),
                    end
                ))
                last = end
            if len(segments) > 0:
                outlines.append(OutlineBezierDto(segments))
        elif command.type == DrawCommandType.QUADRATIC_SYMMETRIC:
            if len(outlines) == 0:
                last = start
            else:
                last = outlines[-1].segments[-1].end
            if len(outlines) == 0:
                raise Exception("can't be first")
            last_outline = outlines[-1]
            last_segment = last_outline.segments[-1]
            if isinstance(last_segment, SegmentBezierDto):
                diff = last_segment.end - last_segment.control2
                control1 = last_segment.end + diff
            elif isinstance(last_segment, SegmentLineDto):
                control1 = last_segment.end
            else:
                raise Exception("unknown segment type")
            segments = []
            for (c2x, c2y, x, y) in list_window(command.arguments, 4):
                control2 = point_to_fcm(c2x, c2y) - offset
                end = point_to_fcm(x, y) - offset
                segments.append(SegmentBezierDto(
                    last + (control1 - last) * (2/3),
                    control2 + (control2 - control1) * (2/3),
                    end
                ))
                last = end
                diff = end - control2
                control1 = end + diff
            if len(segments) > 0:
                outlines.append(OutlineBezierDto(segments))
        elif command.type == DrawCommandType.BEZIER:
            segments = [SegmentBezierDto(
                point_to_fcm(c1x, c1y) - offset, point_to_fcm(c2x, c2y) - offset, point_to_fcm(x, y) - offset
            ) for (c1x, c1y, c2x, c2y, x, y) in list_window(command.arguments, 6)]
            if len(segments) > 0:
                outlines.append(OutlineBezierDto(segments))
        elif command.type == DrawCommandType.BEZIER_SYMMETRIC:
            if len(outlines) == 0:
                raise Exception("can't be first")
            last_outline = outlines[-1]
            last_segment = last_outline.segments[-1]
            if isinstance(last_segment, SegmentBezierDto):
                diff = last_segment.end - last_segment.control2
                control1 = last_segment.end + diff
            elif isinstance(last_segment, SegmentLineDto):
                control1 = last_segment.end
            else:
                raise Exception("unknown segment type")
            segments = []
            for (c2x, c2y, x, y) in list_window(command.arguments, 4):
                control2 = point_to_fcm(c2x, c2y) - offset
                end = point_to_fcm(x, y) - offset
                segments.append(SegmentBezierDto(
                    control1, control2, end
                ))
                diff = end - control2
                control1 = end + diff
            if len(segments) > 0:
                outlines.append(OutlineBezierDto(segments))
        elif command.type == DrawCommandType.VERTICAL_LINE:
            if len(outlines) == 0:
                last = start
            else:
                last = outlines[-1].segments[-1].end
            segments = [SegmentLineDto(PointDto(last.x, int(round(y * 100)) - offset.y)) for y in command.arguments]
            if len(segments) > 0:
                outlines.append(OutlineLineDto(segments))
        elif command.type == DrawCommandType.HORIZONTAL_LINE:
            if len(outlines) == 0:
                last = start
            else:
                last = outlines[-1].segments[-1].end
            segments = [SegmentLineDto(PointDto(int(round(x * 100)) - offset.x, last.y)) for x in command.arguments]
            if len(segments) > 0:
                outlines.append(OutlineLineDto(segments))
        elif command.type == DrawCommandType.LINE:
            segments = [SegmentLineDto(point_to_fcm(x, y) - offset) for (x, y) in list_window(command.arguments, 2)]
            if len(segments) > 0:
                outlines.append(OutlineLineDto(segments))
        elif command.type == DrawCommandType.MOVE:
            if len(outlines) != 0 and start is not None:
                paths.append(PathDto(PathFlagsDto(open=True, tool_cut=True), start - offset, outlines))
            start = point_to_fcm(command.arguments[0], command.arguments[1])
            outlines = []
            segments = [SegmentLineDto(point_to_fcm(x, y) - offset) for (x, y) in list_window(command.arguments[2:], 2)]
            if len(segments) > 0:
                outlines.append(OutlineLineDto(segments))
        elif command.type == DrawCommandType.CLOSE:
            if len(outlines) != 0 and start is not None:
                outlines.append(OutlineLineDto([SegmentLineDto(start - offset)]))
                paths.append(PathDto(PathFlagsDto(open=False, tool_cut=True), start - offset, outlines))
            start = None
            outlines = []
        else:
            raise Exception("Unknown command: " + command.type)
    if len(outlines) != 0 and start is not None:
        paths.append(PathDto(PathFlagsDto(open=True, tool_cut=True), start - offset, outlines))
    return paths

def piece_to_fcm(piece: xml.dom.minidom.Node, label: str = "") -> PieceDto:
    paths = find_elements(piece, tag_name="path")
    paths = [Path.of(path.getAttribute("d")) for path in paths]
    contours = [contour for path in paths for contour in Contour.of(path)]
    min_x = min(contour.min_x() for contour in contours)
    min_y = min(contour.min_y() for contour in contours)
    max_y = max(contour.max_y() for contour in contours)
    max_x = max(contour.max_x() for contour in contours)
    top_left = point_to_fcm(min_x, min_y)
    bottom_right = point_to_fcm(max_x, max_y)
    size = bottom_right - top_left
    center = PointDto(
        (top_left.x + bottom_right.x) // 2,
        (top_left.y + bottom_right.y) // 2,
    )
    paths = [fcm_path for path in paths for fcm_path in path_to_fcm(path, center)]
    paths.sort(key=lambda path: path.start.y)
    sorted_paths = [paths[0]]
    paths = paths[1:]
    while len(paths) > 0:
        last = sorted_paths[-1].outlines[-1].segments[-1].end
        p = min(paths, key=lambda el: math.sqrt(math.pow(last.x - el.start.x, 2) + math.pow((last.y - el.start.y) * 10, 2)))
        paths.remove(p)
        sorted_paths.append(p)
    return PieceDto(size.x, size.y, 0, 0, (1.0, 0.0, 0.0, 1.0, float(center.x), float(center.y)), PieceFlagsDto(seam_allowance_locked=True), label, sorted_paths)


def extract_paths(filename: str) -> FileDto:
    dom = xml.dom.minidom.parse(filename)
    return FileDto(
        content_id=400000002,
        short_name="",
        long_name=" ",
        author_name=" ",
        copyright=" ",
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
            piece_to_fcm(dom, ""),
        ],
    )


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 2:
        converted = extract_paths(args[0])
        with open(args[1], "w") as out:
            json.dump(converted, out, cls=CustomJsonEncoder)
