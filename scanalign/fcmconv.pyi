import enum
from typing import Optional


def to_file(model: FcmFile) -> Optional[str]: ...


class FcmFile:
    header: FileHeader
    cut: CutData
    pieces: list[Piece]

    def __new__(
            cls,
            header: FileHeader,
            cut: CutData,
            pieces: list[Piece]
    ) -> 'FcmFile': ...

    def write(self, file: str) -> Optional[str]: ...

    @classmethod
    def read(cls, file: str) -> FcmFile: ...


class FileHeader:
    variant: FileVariant
    version: str
    content_id: int
    short_name: str
    long_name: str
    author_name: str
    copyright: str
    thumbnail_block_size_width: int
    thumbnail_block_size_height: int
    thumbnail: bytes
    generator: Generator
    print_to_cut: Optional[bool]

    def __new__(
            cls,
            variant: FileVariant,
            version: str,
            content_id: int,
            short_name: str,
            long_name: str,
            author_name: str,
            copyright: str,
            thumbnail_block_size_width: int,
            thumbnail_block_size_height: int,
            thumbnail: bytes,
            generator: Generator,
            print_to_cut: Optional[bool],
    ) -> 'FileHeader': ...


class FileVariant(enum.Enum):
    FCM = ...
    VCM = ...


class Generator:
    class App(Generator):
        version: int

        def __new__(cls, version: int): ...

    class Web(Generator):
        version: int

        def __new__(cls, version: int): ...

    class Device(Generator):
        model: int
        version: int

        def __new__(cls, model: int, version: int): ...


class CutData:
    file_type: FileType
    mat_id: int
    cut_width: int
    cut_height: int
    seam_allowance_width: int
    alignment: Optional[AlignmentData]

    def __new__(
            cls,
            file_type: FileType,
            mat_id: int,
            cut_width: int,
            cut_height: int,
            seam_allowance_width: int,
            alignment: Optional[AlignmentData],
    ) -> 'CutData': ...


class FileType(enum.Enum):
    Cut = ...
    PrintAndCut = ...


class AlignmentData:
    needed: bool
    marks: list[Point]

    def __new__(cls, needed: bool, marks: list[Point]): ...


class Piece:
    width: int
    height: int
    transform: Optional[tuple[float, float, float, float, float, float]]
    expansion_limit_value: int
    reduction_limit_value: int
    restriction_flags: list[PieceRestrictions]
    label: str
    paths: list[Path]

    def __new__(
            cls,
            width: int,
            height: int,
            transform: Optional[tuple[float, float, float, float, float, float]],
            expansion_limit_value: int,
            reduction_limit_value: int,
            restriction_flags: list[PieceRestrictions],
            label: str,
            paths: list[Path],
    ) -> 'Piece': ...


class PieceRestrictions(enum.Enum):
    LicenseDesign = ...
    SeamAllowance = ...
    ProhibitionOfSeamAllowanceSetting = ...
    NoAspectRatioChangeProhibited = ...
    JudgeByUsingPerfectMaskAtAutoLayout = ...
    TestPattern = ...
    ProhibitionOfEdit = ...
    ProhibitionOfTool = ...


class Path:
    tool: list[PathTool]
    shape: Optional[PathShape]
    rhinestone_diameter: Optional[int]
    rhinestones: list[Point]

    def __new__(
            cls,
            tool: list[PathTool],
            shape: Optional[PathShape],
            rhinestone_diameter: Optional[int],
            rhinestones: list[Point],
    ) -> 'Path': ...


class PathTool(enum.Enum):
    PathOpen = ...
    ToolCut = ...
    ToolDraw = ...
    SeamAllowance = ...
    ToolRhinestone = ...
    Fill = ...
    AutoAlign = ...
    ToolDrawOnly = ...
    ToolEmboss = ...
    ToolFoil = ...
    ToolPerforating = ...


class PathShape:
    start: Point
    outlines: list[Outline]

    def __new__(
            cls,
            start: Point,
            outlines: list[Outline],
    ) -> 'PathShape': ...


class Outline:
    class Line(Outline):
        segments: list[Point]

        def __new__(cls, segments: list[Point]): ...

    class Bezier(Outline):
        segments: list[Segment]

        def __new__(cls, segments: list[Segment]): ...


class Segment:
    control1: Point
    control2: Point
    end: Point

    def __new__(cls, control1: Point, control2: Point, end: Point): ...


class Point:
    x: int
    y: int

    def __new__(
            cls,
            x: int,
            y: int,
    ) -> 'Point': ...
