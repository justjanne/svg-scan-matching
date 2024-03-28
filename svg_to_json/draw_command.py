import enum
import re
from typing import NamedTuple


class DrawCommandType(enum.StrEnum):
    MOVE = "M"
    LINE = "L"
    HORIZONTAL_LINE = "H"
    VERTICAL_LINE = "V"
    BEZIER = "C"
    BEZIER_SYMMETRIC = "S"
    QUADRATIC = "Q"
    QUADRATIC_SYMMETRIC = "T"
    ARC = "A"
    CLOSE = "Z"

    @classmethod
    def has(cls, item):
        return cls._value2member_map_.__contains__(item)


class DrawCommand(NamedTuple):
    type: DrawCommandType
    absolute: bool = True
    arguments: list[float] = []

    def to_string(self) -> str:
        command_type = self.type.value
        if not self.absolute:
            command_type = command_type.lower()

        return "{0} {1}".format(
            command_type,
            " ".join("{0:g}".format(arg) for arg in self.arguments)
        )

    @staticmethod
    def of(command: str, arguments: str):
        arguments = arguments.strip()
        arguments = re.split(r" +|,", arguments)
        arguments = [arg.strip() for arg in arguments]
        arguments = [float(arg) for arg in arguments if len(arg) != 0]
        return DrawCommand(DrawCommandType(command.upper()), command.isupper(), arguments)
