from typing import NamedTuple


class Coordinate(NamedTuple):
    x: float
    y: float

    def __add__(self, other):
        return Coordinate(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Coordinate(self.x - other.x, self.y - other.y)
