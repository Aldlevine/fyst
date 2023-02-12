from collections import UserList
from typing import NamedTuple, TypeVar

class Point(NamedTuple):
    x: int
    y: int

point_ = Point | tuple[int, int] | list[int]


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
        grid[:,:] = value
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
                col.extend([value]*(nh-oh))
        elif oh > nh:
            for i, col in enumerate(self):
                self.data[i] = col[:nh]

        if ow < nw:
            new_col: list[T] = [value] * nh
            new_cols = [new_col.copy() for _ in range(nw-ow)]
            self.data.extend(new_cols)
        elif ow > nw:
            for _ in range(nw, ow):
                self.pop()

        return self

    def transpose(self) -> "Grid[T]":
        col: list[T] = [None]*self.width # type: ignore
        data: list[list[T]] = [col.copy() for _ in range(self.height)]
        for x in range(self.width):
            for y in range(self.height):
                data[y][x] = self.data[x][y]
        self.data = data
        return self

    def paste(self, pos: point_, grid: "Grid[T]") -> "Grid[T]":
        x, y = pos
        w, h = grid.size
        self[x:x+w, y:y+h] = grid
        return self

    def item(self) -> T | None:
        if self.width != 1 or self.height != 1: raise IndexError
        return self.data[0][0]

    # TODO: figure out broadcasting to standardize these types of methods
    def __or__(self, other: "Grid[T]") -> "Grid[T]":
        if self.size != other.size:
            raise IndexError
        if self.size.x == 0 or self.size.y == 0:
            return self[:,:]
        data: list[list[T]] = []
        for i, col in enumerate(self.data):
            other_col = other.data[i]
            data.append([a | b for a,b in zip(col, other_col)]) # type: ignore
        return Grid[T](data)

    def __and__(self, other: "Grid[T]") -> "Grid[T]":
        if self.size != other.size:
            raise IndexError
        if self.size.x == 0 or self.size.y == 0:
            return self[:,:]
        data: list[list[T]] = []
        for i, col in enumerate(self.data):
            other_col = other.data[i]
            data.append([a & b for a,b in zip(col, other_col)]) # type: ignore
        return Grid[T](data)

    def __repr__(self) -> str:
        l: list[str] = []
        for y in range(self.height):
            s = ""
            for x in range(self.width):
                s += str(self.data[x][y])
            l.append(s)
        return "\n".join(l)
        

    def __getitem__(self,
        pos: point_ | int | slice | tuple[int, int] | tuple[int, slice] | tuple[slice, int] | tuple[slice, slice],
    ) -> "Grid[T]":
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

    def _setitem_buffer(
        self,
        pos: point_ | int | slice | tuple[int, int] | tuple[int, slice] | tuple[slice, int] | tuple[slice, slice],
        val: "Grid[T]",
    ) -> None:
        # self[#]
        if isinstance(pos, int):
            if val.height != self.height: raise IndexError

            if val.width != 1: raise
            self.data[pos] = val.data[0]
            return

        # self[#:#:#]
        if isinstance(pos, slice):
            if val.height != self.height: raise IndexError

            if val.width == 1:
                self.data[pos] = [val.data[0]] * len(self.data[pos])
            else:
                if val.width != len(self.data[pos]): raise IndexError
                self.data[pos] = val.data
            return


        x, y = pos

        # self[#, #]
        if isinstance(x, int) and isinstance(y, int):
            if val.width != 1 or val.height != 1:
                self.paste((x, y), val)
            self.data[x][y] = val.data[0][0]

        # self[#, #:#:#]
        if isinstance(x, int) and isinstance(y, slice):
            if val.width != 1: raise IndexError
            if val.height != len(self.data[x][y]): raise IndexError
            self.data[x][y] = val.data[0]

        # self[#:#:#, #]
        if isinstance(x, slice) and isinstance(y, int):
            rows = self.data[x]
            if val.width != len(rows): raise IndexError
            if val.height != 1: raise IndexError
            for i, row in enumerate(rows):
                row[y] = val.data[i][0]

        # self[#:#:#, #:#:#]
        if isinstance(x, slice) and isinstance(y, slice):
            rows = self.data[x]
            if val.width != len(rows): raise IndexError
            if val.height != len(rows[0][y]): raise IndexError
            for i, row in enumerate(rows):
                row[y] = val.data[i]

    def _setitem_element(
        self,
        pos: point_ | int | slice | tuple[int, int] | tuple[int, slice] | tuple[slice, int] | tuple[slice, slice],
        val: T
    ) -> None:
        # self[#]
        if isinstance(pos, int):
            self.data[pos] = [val] * self.height
            return

        # self[#:#:#]
        if isinstance(pos, slice):
            x = [[val] * self.height] * len(self.data[pos])
            self.data[pos] = x
            return

        y, x = pos

        # self[#, #]
        if isinstance(y, int) and isinstance(x, int):
            # if val.height() != 1 and val.width() != 1: raise IndexError
            self.data[y][x] = val
            return

        # self[#, #:#:#]
        if isinstance(y, int) and isinstance(x, slice):
            self.data[y][x] = [val] * len(self.data[y][x])
            return

        # self[#:#:#, #]
        if isinstance(y, slice) and isinstance(x, int):
            rows = self.data[y]
            for row in rows:
                row[x] = val
            return

        # self[#:#:#, #:#:#]
        if isinstance(y, slice) and isinstance(x, slice):
            rows = self.data[y]
            for row in rows:
                row[x] = [val] * len(row[x])
            return

    def __setitem__(
        self,
        pos: point_ | int | slice | tuple[int, int] | tuple[int, slice] | tuple[slice, int] | tuple[slice, slice],
        val: T | "Grid[T]"
    ) -> None:
        if isinstance(val, Grid):
            self._setitem_buffer(pos, val) # type: ignore
        else:
            self._setitem_element(pos, val)

