from __future__ import annotations

import abc
from enum import Enum
from typing import List, Iterator, Iterable

from attr import dataclass


@dataclass(frozen=True)
class Point:
    x: int
    y: int


class CeilState(Enum):
    DEAD = 0
    ALIVE = 1


class IBoard(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def height(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def width(self) -> int:
        pass

    @abc.abstractmethod
    def get(self, point: Point) -> CeilState:
        pass


class Board(IBoard):
    def __init__(self, width: int, height: int):
        self._width = width
        self._height = height
        self._array = [
            [CeilState.DEAD for _ in range(width)]
            for _ in range(height)
        ]

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def to_array(self) -> List[List[CeilState]]:
        return self._array

    def mark_alive(self, point: Point) -> None:
        point = self._get_safe_point(point)
        self._array[point.y][point.x] = CeilState.ALIVE

    def mark_dead(self, point: Point) -> None:
        point = self._get_safe_point(point)
        self._array[point.y][point.x] = CeilState.DEAD

    def get(self, point: Point) -> CeilState:
        point = self._get_safe_point(point)
        return self._array[point.y][point.x]

    def get_neighbors(self, point: Point) -> Iterator[CeilState]:
        point = self._get_safe_point(point)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                _p = self._get_safe_point(Point(
                    point.x + dx,
                    point.y + dy
                ))
                yield self._array[_p.y][_p.x]

    def _get_safe_point(self, point: Point):
        return Point(x=point.x % self._width, y=point.y % self._height)

    def __eq__(self, other: IBoard):
        if self.height != other.height or self.width != other.width:
            return False

        for point in self.iter_points():
            if self.get(point) != other.get(point):
                return False
        return True

    def __repr__(self):
        return "\n{}\n".format(
            "\n".join(
                ' '.join(str(ceil.value) for ceil in row)
                for row in self._array
            )
        )

    def iter_points(self):
        for y in range(self.height):
            for x in range(self.width):
                yield Point(x, y)


def is_empty(array) -> bool:
    for line in array:
        for ceil in line:
            if ceil is CeilState.ALIVE:
                return False
    return True


def get_next_board(board: Board) -> Board:
    new_board = Board(board.width, board.height)

    for point in board.iter_points():
        count_neighbors = len(filter_alive(board.get_neighbors(point)))
        if count_neighbors == 3:
            new_board.mark_alive(point)
        elif count_neighbors == 2 and board.get(point) is CeilState.ALIVE:
            new_board.mark_alive(point)

    return new_board


def filter_alive(state_seq: Iterable[CeilState]):
    return list(filter(lambda i: i is CeilState.ALIVE, state_seq))
