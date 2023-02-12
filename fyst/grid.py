from collections import UserList
from typing import NamedTuple, TypeVar


class Point(NamedTuple):
    x: int
    y: int


point_ = Point | tuple[int, int] | list[int]

_broadcastable = (point_ | int | slice | tuple[int, slice] | tuple[slice, int]
                  | tuple[slice, slice])

T = TypeVar("T")


class Grid(UserList[list[T]]):

    @classmethod
    def from_str(cls, s: str, blank: str = " ") -> "Grid[str]":
        data: list[list[str]] = [list(l) for l in s.split("\n")]
        w = 0
        for col in data:
            w = max(w, len(col))
        for col in data:
            col.extend([blank] * (w - len(col)))

        return Grid(data).transpose()

    @classmethod
    def full(cls, size: point_, value: T) -> "Grid[T]":
        grid = Grid[T]()
        grid.resize(size, value)
        grid[:, :] = value
        return grid

    @property
    def width(self) -> int:
        return len(self.data)

    @property
    def height(self) -> int:
        if len(self) == 0:
            return 0
        return len(self.data[0])

    @property
    def size(self) -> Point:
        return Point(self.width, self.height)

    def resize(self, new_size: point_, value: T) -> "Grid[T]":
        ow, oh = self.size
        nw, nh = new_size

        if oh < nh:
            for col in self:
                col.extend([value] * (nh - oh))
        elif oh > nh:
            for i, col in enumerate(self):
                self.data[i] = col[:nh]

        if ow < nw:
            new_col: list[T] = [value] * nh
            new_cols = [new_col.copy() for _ in range(nw - ow)]
            self.data.extend(new_cols)
        elif ow > nw:
            for _ in range(nw, ow):
                self.pop()

        return self

    def transpose(self) -> "Grid[T]":
        col: list[T] = [None] * self.width  # type: ignore
        data: list[list[T]] = [col.copy() for _ in range(self.height)]
        for x in range(self.width):
            for y in range(self.height):
                data[y][x] = self.data[x][y]
        self.data = data
        return self

    def copy(self) -> "Grid[T]":
        data: list[list[T]] = [c.copy() for c in self.data]
        return Grid(data)

    def repeat(self, size: point_) -> "Grid[T]":
        x, y = size
        if y > 1:
            for i, col in enumerate(self.data):
                self.data[i] = col * y
        new_cols: list[list[T]] = []
        for i in range(1, x):
            new_cols.extend(self.copy().data)
        self.data.extend(new_cols)
        return self

    def paste(self, pos: point_, grid: "Grid[T]") -> "Grid[T]":
        x, y = pos
        w, h = grid.size
        self[x:x + w, y:y + h] = grid
        return self

    def item(self) -> T:
        if self.width != 1 or self.height != 1: raise IndexError
        return self.data[0][0]

    # TODO: figure out broadcasting to standardize these types of methods
    def __or__(self, other: "Grid[T]") -> "Grid[T]":
        if self.size != other.size:
            raise IndexError
        if self.size.x == 0 or self.size.y == 0:
            return self[:, :]
        data: list[list[T]] = []
        for i, col in enumerate(self.data):
            other_col = other.data[i]
            data.append([
                a | b  # type: ignore
                for a, b in zip(col, other_col)
            ])
        return Grid[T](data)

    def __and__(self, other: "Grid[T]") -> "Grid[T]":
        if self.size != other.size:
            raise IndexError
        if self.size.x == 0 or self.size.y == 0:
            return self[:, :]
        data: list[list[T]] = []
        for i, col in enumerate(self.data):
            other_col = other.data[i]
            data.append([
                a & b  # type: ignore
                for a, b in zip(col, other_col)
            ])
        return Grid[T](data)

    def __repr__(self) -> str:
        l: list[str] = []
        for y in range(self.height):
            s = ""
            for x in range(self.width):
                s += str(self.data[x][y])
            l.append(s)
        return "\n".join(l)

    def _broadcast_grid(
        self,
        pos: _broadcastable,
        val: "Grid[T]",
    ) -> tuple[tuple[slice, slice], "Grid[T]"]:
        # self[#:#:#]
        if isinstance(pos, int):
            pos = slice(pos, pos + 1)
        if isinstance(pos, slice):
            x_repeat = len(self.data[pos]) if val.width == 1 else 1
            y_repeat = self.height if val.height == 1 else 1
            if x_repeat > 1 or y_repeat > 1:
                val = val.copy().repeat((x_repeat, y_repeat))

            if val.height != self.height: raise IndexError
            if val.width != len(self.data[pos]): raise IndexError

            x_slice = pos
            y_slice = slice(None)
            return (x_slice, y_slice), val

        # self[#:#:#, #:#:#]
        x, y = pos

        # paste
        if isinstance(x, int) and isinstance(y, int):
            x = slice(x, x + val.width)
            y = slice(y, y + val.height)
            return (x, y), val

        if isinstance(x, int):
            x = slice(x, x + 1 if x != -1 else None)
        if isinstance(y, int):
            y = slice(y, y + 1 if y != -1 else None)
        x_repeat = len(self.data[x]) if val.width == 1 else 1
        y_repeat = len(self.data[0][y]) if val.height == 1 else 1
        if x_repeat > 1 or y_repeat > 1:
            val = val.copy().repeat((x_repeat, y_repeat))
        if val.width != len(self.data[x]): raise IndexError
        if val.height != len(self.data[0][y]): raise IndexError
        return (x, y), val

    def _broadcast(
        self,
        pos: _broadcastable,
        val: T | "Grid[T]",
    ) -> tuple[tuple[slice, slice], "Grid[T]"]:
        if isinstance(val, Grid):
            return self._broadcast_grid(pos, val)  # type: ignore
        else:
            return self._broadcast_grid(pos, Grid([[val]]))

    # TODO: return grid view instead of copy
    def __getitem__(self, pos: _broadcastable) -> "Grid[T]":
        if isinstance(pos, slice):
            start, stop, stride = pos.indices(self.width)
            cols = self.data[start:stop:stride]
            return self.__class__(cols)
        if isinstance(pos, int):
            cols = [self.data[pos]]
            return self.__class__(cols)

        x, y = pos
        cols: list[list[T]]
        if isinstance(x, slice):
            start, stop, stride = x.indices(self.width)
            cols = self.data[start:stop:stride]
        else:
            cols = [self.data[x]]

        if isinstance(y, slice):
            return self.__class__([col[y] for col in cols])

        return self.__class__([[col[y]] for col in cols])

    def __setitem__(self, pos: _broadcastable, val: T | "Grid[T]") -> None:
        (x, y), val = self._broadcast(pos, val)
        cols = self.data[x]
        for i, row in enumerate(cols):
            row[y] = val.data[i]
