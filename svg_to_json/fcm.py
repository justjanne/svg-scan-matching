import enum
from dataclasses import dataclass


@dataclass
class PointDto:
    x: int
    y: int

    def __add__(self, other):
        return PointDto(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return PointDto(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return PointDto(int(round(self.x * other)), int(round(self.y * other)))


@dataclass
class SegmentLineDto:
    end: PointDto


@dataclass
class SegmentBezierDto:
    control1: PointDto
    control2: PointDto
    end: PointDto


class OutlineTypeDto(enum.StrEnum):
    LINE = "line"
    BEZIER = "bezier"


@dataclass
class OutlineLineDto:
    segments: list[SegmentLineDto]
    type: OutlineTypeDto = OutlineTypeDto.LINE


@dataclass
class OutlineBezierDto:
    segments: list[SegmentBezierDto]
    type: OutlineTypeDto = OutlineTypeDto.BEZIER


OutlineDto = OutlineLineDto | OutlineBezierDto


@dataclass
class PathFlagsDto:
    open: bool = False
    fill: bool = False
    seam_allowance: bool = False
    auto_align: bool = False
    tool_cut: bool = False
    tool_draw: bool = False
    tool_draw_only: bool = False
    tool_rhinestone: bool = False
    tool_emboss: bool = False
    tool_foil: bool = False
    tool_perforating: bool = False


@dataclass
class PathDto:
    flags: PathFlagsDto
    start: PointDto
    outlines: list[OutlineDto]


@dataclass
class PieceFlagsDto:
    licensed: bool = False
    seam_allowance_enabled: bool = False
    seam_allowance_locked: bool = False
    aspect_ratio_locked: bool = False
    test_pattern: bool = False
    path_locked: bool = False
    tool_locked: bool = False


@dataclass
class PieceDto:
    width: int
    height: int
    expansion_limit: int
    reduction_limit: int
    transform: tuple[float, float, float, float, float, float] | None
    flags: PieceFlagsDto
    label: str
    paths: list[PathDto]


@dataclass
class CutDataDto:
    mat_id: int
    cut_width: int
    cut_height: int
    seam_allowance_width: int


@dataclass
class ThumbnailDto:
    block_width: int
    block_height: int
    data: bytes


@dataclass
class FileDto:
    content_id: int
    short_name: str
    long_name: str
    author_name: str
    copyright: str
    cut_data: CutDataDto
    thumbnail: ThumbnailDto
    pieces: list[PieceDto]
