from typing import NamedTuple

from coordinate import Coordinate
from draw_command import DrawCommand, DrawCommandType
from path import Path


def list_window(collection: list, size: int) -> list[tuple]:
    return [tuple(collection[i:i + size]) for i in range(0, len(collection) - size + 1, size)]


class Contour(NamedTuple):
    points: list[Coordinate]
    closed: bool

    def min_x(self) -> float:
        return min(x for (x, _) in self.points)

    def min_y(self) -> float:
        return min(y for (_, y) in self.points)

    def max_x(self) -> float:
        return max(x for (x, _) in self.points)

    def max_y(self) -> float:
        return max(y for (_, y) in self.points)

    def bounding_box(self):
        return Contour([
            Coordinate(self.min_x(), self.min_y()),
            Coordinate(self.max_x(), self.min_y()),
            Coordinate(self.max_x(), self.max_y()),
            Coordinate(self.min_x(), self.max_y()),
        ], True)

    def to_path(self) -> Path:
        arguments = []
        for (x, y) in self.points:
            arguments.append(x)
            arguments.append(y)

        if self.closed:
            return Path([
                DrawCommand(DrawCommandType.MOVE, True, arguments),
                DrawCommand(DrawCommandType.CLOSE)
            ])
        else:
            return Path([
                DrawCommand(DrawCommandType.MOVE, True, arguments),
            ])

    @staticmethod
    def of(path: Path):
        outlines: list[Contour] = []
        points: list[Coordinate] = []

        def last_point() -> Coordinate:
            if len(points) > 0:
                return points[-1]
            if len(outlines) > 0:
                return outlines[-1].points[-1]
            else:
                return Coordinate(0, 0)

        for command in path.commands:
            if command.type == DrawCommandType.MOVE:
                if len(points) != 0:
                    outlines.append(Contour(points, False))
                    points = []
                for (x, y) in list_window(command.arguments, 2):
                    point = Coordinate(x, y)
                    if not command.absolute:
                        point += last_point()
                    points.append(point)
            elif command.type == DrawCommandType.LINE:
                for (x, y) in list_window(command.arguments, 2):
                    point = Coordinate(x, y)
                    if not command.absolute:
                        point += last_point()
                    points.append(point)
            elif command.type == DrawCommandType.HORIZONTAL_LINE:
                for x in command.arguments:
                    previous = last_point()
                    if command.absolute:
                        point = Coordinate(x, previous.y)
                    else:
                        point = Coordinate(x + previous.x, previous.y)
                    points.append(point)
            elif command.type == DrawCommandType.VERTICAL_LINE:
                for y in command.arguments:
                    previous = last_point()
                    if command.absolute:
                        point = Coordinate(previous.x, y)
                    else:
                        point = Coordinate(previous.x, y + previous.y)
                    points.append(point)
            elif command.type == DrawCommandType.BEZIER:
                for (_, _, _, _, x, y) in list_window(command.arguments, 6):
                    point = Coordinate(x, y)
                    if not command.absolute:
                        point += last_point()
                    points.append(point)
            elif command.type == DrawCommandType.BEZIER_SYMMETRIC:
                for (_, _, x, y) in list_window(command.arguments, 4):
                    point = Coordinate(x, y)
                    if not command.absolute:
                        point += last_point()
                    points.append(point)
            elif command.type == DrawCommandType.QUADRATIC:
                for (_, _, x, y) in list_window(command.arguments, 4):
                    point = Coordinate(x, y)
                    if not command.absolute:
                        point += last_point()
                    points.append(point)
            elif command.type == DrawCommandType.QUADRATIC_SYMMETRIC:
                for (x, y) in list_window(command.arguments, 2):
                    point = Coordinate(x, y)
                    if not command.absolute:
                        point += last_point()
                    points.append(point)
            elif command.type == DrawCommandType.ARC:
                for (_, _, _, _, _, x, y) in list_window(command.arguments, 7):
                    point = Coordinate(x, y)
                    if not command.absolute:
                        point += last_point()
                    points.append(point)
            elif command.type == DrawCommandType.CLOSE:
                if len(points) != 0:
                    if len(points) > 1:
                        points.append(points[0])
                    outlines.append(Contour(points, True))
                    points = []
        if len(points) != 0:
            outlines.append(Contour(points, False))
        return outlines
