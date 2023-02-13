from __future__ import annotations

from collections import UserList
from typing import NamedTuple, TypeVar


class Point(NamedTuple):
    x: int
    y: int


point_ = Point | tuple[int, int] | list[int]

_broadcastable = (point_ | int | slice | tuple[int, slice] | tuple[slice, int]
                  | tuple[slice, slice])

T = TypeVar("T")

_col = list[T]
_data = list[_col[T]]


class View(NamedTuple):
    x: slice = slice(None)
    y: slice = slice(None)


def _combine_slices(length: int, *slices: slice):
    r = range(length)
    for s in slices:
        r = r[s]
    return slice(r.start, r.stop, r.step)


class Grid(UserList[list[T]]):

    def __init__(
            self,
            data: _data[T] = [],
            view: View = View(),
    ) -> None:
        super().__init__(data)
        self.view = view

    @classmethod
    def from_str(cls, s: str, blank: str = " ") -> Grid[str]:
        data: list[list[str]] = [list(l) for l in s.split("\n")]
        w = 0
        for col in data:
            w = max(w, len(col))
        for col in data:
            col.extend([blank] * (w - len(col)))

        return Grid(data).transpose()

    @classmethod
    def full(cls, size: point_, value: T) -> Grid[T]:
        x, y = size
        data = [[value] * y for _ in range(x)]
        grid = Grid[T](data)
        return grid

    @property
    def width(self) -> int:
        return len(self.data[self.view.x])

    @property
    def height(self) -> int:
        if len(self) == 0:
            return 0
        return len(self.data[0][self.view.y])

    @property
    def size(self) -> Point:
        return Point(self.width, self.height)

    def transpose(self) -> Grid[T]:
        col: list[T] = [None] * self.width  # type: ignore
        data: list[list[T]] = [col.copy() for _ in range(self.height)]
        for x in range(self.width):
            for y in range(self.height):
                data[y][x] = self.data[x][y]
        self.data = data
        return self

    def repeat(self, size: point_) -> Grid[T]:
        x, y = size
        if y > 1:
            for i, col in enumerate(self.data):
                self.data[i] = col * y
        new_cols: list[list[T]] = []
        for i in range(1, x):
            new_cols.extend(self.copy().data)
        self.data.extend(new_cols)
        return self

    # non mutating

    def copy(self) -> Grid[T]:
        return Grid(self._get_view_data())

    def item(self) -> T:
        if self.width != 1 or self.height != 1: raise IndexError
        return self._get_view_data()[0][0]

    def _get_view_data(self, subview: View | None = None) -> list[list[T]]:
        x = _combine_slices(self.width, self.view.x,
                           subview.x) if subview != None else self.view.x
        y = _combine_slices(self.height, self.view.y,
                           subview.y) if subview != None else self.view.y
        data: list[list[T]] = [c[y] for c in self.data[x]]
        return data

    def __or__(self, other: Grid[T] | T) -> Grid[T]:
        _, other = self._broadcast(View(), other)
        if self.size != other.size:
            raise IndexError
        if self.size.x == 0 or self.size.y == 0:
            return self.copy()
        data: list[list[T]] = []
        vself = self._get_view_data()
        vother = other._get_view_data()
        for i, col in enumerate(vself):
            other_col = vother[i]
            data.append([
                a | b  # type: ignore
                for a, b in zip(col, other_col)
            ])
        return Grid[T](data)

    def __and__(self, other: Grid[T] | T) -> Grid[T]:
        _, other = self._broadcast(View(), other)
        if self.size != other.size:
            raise IndexError
        if self.size.x == 0 or self.size.y == 0:
            return self.copy()
        data: list[list[T]] = []
        vself = self._get_view_data()
        vother = other._get_view_data()
        for i, col in enumerate(vself):
            other_col = vother[i]
            data.append([
                a & b  # type: ignore
                for a, b in zip(col, other_col)
            ])
        return Grid[T](data)

    def __repr__(self) -> str:
        l: list[str] = []
        vself = self._get_view_data()
        for y in range(self.height):
            s = ""
            for x in range(self.width):
                s += str(vself[x][y])
            l.append(s)
        return "\n".join(l)

    def _broadcast_grid(
        self,
        pos: _broadcastable,
        other: Grid[T],
    ) -> tuple[tuple[slice, slice], Grid[T]]:
        vself = self._get_view_data()
        # self[#:#:#]
        if isinstance(pos, int):
            pos = slice(pos, pos + 1 if pos != -1 else None)
        if isinstance(pos, slice):
            x_repeat = len(vself[pos]) if other.width == 1 else 1
            y_repeat = self.height if other.height == 1 else 1
            if x_repeat > 1 or y_repeat > 1:
                other = other.copy().repeat((x_repeat, y_repeat))

            if other.height != self.height: raise IndexError
            if other.width != len(vself[pos]): raise IndexError

            x = pos
            y = slice(None)
            return (
                _combine_slices(self.width, self.view.x, x),
                _combine_slices(self.height, self.view.y, y),
            ), other

        # self[#:#:#, #:#:#]
        x, y = pos

        # paste
        if isinstance(x, int) and isinstance(y, int):
            x = slice(x, x + other.width if x + other.width != 0 else None)
            y = slice(y, y + other.height if y + other.height != 0 else None)
            return (
                _combine_slices(self.width, self.view.x, x),
                _combine_slices(self.height, self.view.y, y),
            ), other

        if isinstance(x, int):
            x = slice(x, x + 1 if x != -1 else None)
        if isinstance(y, int):
            y = slice(y, y + 1 if y != -1 else None)
        w = len(vself[x])
        h = len(vself[0][y])
        x_repeat = w if other.width == 1 else 1
        y_repeat = h if other.height == 1 else 1
        if x_repeat > 1 or y_repeat > 1:
            other = other.copy().repeat((x_repeat, y_repeat))
        if other.width != w: raise IndexError
        if other.height != h: raise IndexError
        return (
            _combine_slices(self.width, self.view.x, x),
            _combine_slices(self.height, self.view.y, y),
        ), other

    def _broadcast(
        self,
        pos: _broadcastable,
        val: T | Grid[T],
    ) -> tuple[tuple[slice, slice], Grid[T]]:
        if isinstance(val, Grid):
            return self._broadcast_grid(pos, val)  # type: ignore
        else:
            return self._broadcast_grid(pos, Grid[T]([[val]]))

    def __getitem__(self, pos: _broadcastable) -> Grid[T]:
        if isinstance(pos, int):
            pos = slice(pos, pos + 1 if pos != -1 else None)
        if isinstance(pos, slice):
            x = _combine_slices(len(self.data), self.view.x, pos)
            grid = Grid(self.data, view=View(x))
            return grid

        x, y = pos
        if isinstance(x, int):
            x = slice(x, x + 1 if x != -1 else None)
        if isinstance(y, int):
            y = slice(y, y + 1 if y != -1 else None)
        x = _combine_slices(len(self.data), self.view.x, x)
        y = _combine_slices(len(self.data[0]), self.view.y, y)
        grid = Grid(self.data, view=View(x, y))
        return grid

    def __setitem__(self, pos: _broadcastable, val: T | Grid[T]) -> None:
        (x, y), val = self._broadcast(pos, val)
        vdata = val._get_view_data()
        for i, col in enumerate(self.data[x]):
            col[y] = vdata[i]