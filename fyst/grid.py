from __future__ import annotations as _annotations

from collections import UserList as _UserList
from typing import NamedTuple as _NamedTuple
from typing import TypeVar as _TypeVar


class Point(_NamedTuple):
    x: int
    y: int


PointArg = Point | tuple[int, int] | list[int]

_broadcastable = (PointArg | int | slice | tuple[int, slice]
                  | tuple[slice, int]
                  | tuple[slice, slice])

T = _TypeVar("T")

_col = list[T]
_data = list[_col[T]]


class _View(_NamedTuple):
    x: slice = slice(None)
    y: slice = slice(None)


def _combine_slices(length: int, *slices: slice):
    r = range(length)
    for s in slices:
        r = r[s]
    return slice(r.start, r.stop, r.step)


class Grid(_UserList[list[T]]):

    def __init__(
            self,
            data: _data[T] = [],
            view: _View = _View(),
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
        data = [[row[i] for row in data] for i in range(len(data[0]))]

        return Grid(data)

    @classmethod
    def full(cls, size: PointArg, value: T) -> Grid[T]:
        x, y = size
        data = [[value] * y for _ in range(x)]
        grid = Grid[T](data)
        return grid

    @property
    def root_width(self) -> int:
        return len(self.data)

    @property
    def root_height(self) -> int:
        if len(self) == 0:
            return 0
        return len(self.data[0])

    @property
    def width(self) -> int:
        return len(range(*self.view.x.indices(self.root_width)))

    @property
    def height(self) -> int:
        return len(range(*self.view.y.indices(self.root_height)))

    @property
    def size(self) -> Point:
        return Point(self.width, self.height)

    def transpose(self) -> Grid[T]:
        data = self._get_view_data()
        data = [[col[y] for col in data] for y in range(self.height)]
        return Grid(data)

    def repeat(self, size: PointArg) -> Grid[T]:
        x, y = size
        data = self._get_view_data()
        data = [data[i] * y for _ in range(x) for i in range(len(data))]
        return Grid[T](data)

    def copy(self) -> Grid[T]:
        return Grid(self._get_view_data())

    def item(self) -> T:
        if self.width != 1 or self.height != 1: raise IndexError
        return self._get_view_data()[0][0]

    def _get_view_data(self, subview: _View | None = None) -> list[list[T]]:
        x = _combine_slices(self.width, self.view.x,
                            subview.x) if subview != None else self.view.x
        y = _combine_slices(self.height, self.view.y,
                            subview.y) if subview != None else self.view.y
        data: list[list[T]] = [c[y] for c in self.data[x]]
        return data

    def __or__(self, other: Grid[T] | T) -> Grid[T]:
        _, other = self._broadcast(_View(), other)
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
        _, other = self._broadcast(_View(), other)
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
                _combine_slices(self.root_width, self.view.x, x),
                _combine_slices(self.root_height, self.view.y, y),
            ), other

        # self[#:#:#, #:#:#]
        x, y = pos

        # paste
        if isinstance(x, int) and isinstance(y, int):
            x = slice(x, x + other.width if x + other.width != 0 else None)
            y = slice(y, y + other.height if y + other.height != 0 else None)
            return (
                _combine_slices(self.root_width, self.view.x, x),
                _combine_slices(self.root_height, self.view.y, y),
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
            _combine_slices(self.root_width, self.view.x, x),
            _combine_slices(self.root_height, self.view.y, y),
        ), other

    def _broadcast(
        self,
        pos: _broadcastable,
        other: T | Grid[T],
    ) -> tuple[tuple[slice, slice], Grid[T]]:
        if isinstance(other, Grid):
            return self._broadcast_grid(pos, other)  # type: ignore
        else:
            return self._broadcast_grid(pos, Grid[T]([[other]]))

    def __getitem__(self, pos: _broadcastable) -> Grid[T]:
        if isinstance(pos, int):
            pos = slice(pos, pos + 1 if pos != -1 else None)
        if isinstance(pos, slice):
            x = _combine_slices(self.root_width, self.view.x, pos)
            grid = Grid(self.data, view=_View(x))
            return grid

        x, y = pos
        if isinstance(x, int):
            x = slice(x, x + 1 if x != -1 else None)
        if isinstance(y, int):
            y = slice(y, y + 1 if y != -1 else None)
        x = _combine_slices(self.root_width, self.view.x, x)
        y = _combine_slices(self.root_height, self.view.y, y)
        grid = Grid(self.data, view=_View(x, y))
        return grid

    def __setitem__(self, pos: _broadcastable, other: T | Grid[T]) -> None:
        (x, y), other = self._broadcast(pos, other)
        ox = 0
        for sx in range(*x.indices(self.root_width)):
            oy = 0
            for sy in range(*y.indices(self.root_height)):
                self.data[sx][sy] = other[ox, oy].item()
                oy += 1
            ox += 1