from collections import UserList
from enum import IntFlag
from typing import Generic, Literal, NamedTuple, TypeVar

from grid import Grid, Point, point_
from style import BOX_STYLE, DBL_VERT_BOX_STYLE, TableStyle

V = TypeVar("V")


class _Edges(Generic[V]):

    def __init__(
        self,
        *v: V,
    ) -> None:
        if len(v) == 1:
            self.l = v[0]
            self.t = v[0]
            self.r = v[0]
            self.b = v[0]
            return
        if len(v) == 2:
            self.l, self.t = v
            self.r, self.b = v
            return
        if len(v) == 4:
            self.l, self.t, self.r, self.b = v
            return
        raise ValueError


_edges = _Edges[V] | tuple[V, V, V, V] | tuple[V, V] | V


class Padding(_Edges[int]):
    pass


_padding = Padding | tuple[int, int, int, int] | tuple[int, int] | int


class Border(_Edges[bool]):
    pass


_border = Border | tuple[bool, bool, bool, bool] | tuple[bool, bool] | bool


class RCSizes(NamedTuple):
    rows: list[int]
    cols: list[int]


_valign = Literal["top"] | Literal["middle"] | Literal["bottom"]
_halign = Literal["left"] | Literal["middle"] | Literal["right"]


class _Con(IntFlag):
    N = 0
    L = 1
    U = 2
    R = 4
    D = 8


class Cel:

    def __init__(
        self,
        value: str = "",
        span: point_ = (1, 1),
        padding: _padding = (2, 0),
        border: _border = True,
        # TODO: implement alignment
        halign: _halign = "left",
        valign: _valign = "top",
    ) -> None:
        super().__init__()
        self.value = value
        self.span = Point(*span)

        if isinstance(padding, Padding):
            self.padding = padding
        elif isinstance(padding, tuple):
            self.padding = Padding(*padding)
        else:
            self.padding = Padding(padding)

        if isinstance(border, Border):
            self.border = border
        elif isinstance(border, tuple):
            self.border = Border(*border)
        else:
            self.border = Border(border)

    def get_min_size(self, table: "Table") -> Point:
        bw = table.style.w
        s = str(self.value)
        lines = s.split("\n")
        w, h = 0, len(lines)
        for l in lines:
            w = max(len(l), w)
        return Point(
            w + self.padding.l + self.padding.r +
            int(1 or self.border.l or self.border.r) * bw,
            h + self.padding.t + self.padding.b +
            int(1 or self.border.t or self.border.b),
        )

    def draw(
        self,
        grid: Grid[str],
        b_grid: Grid[_Con],
        table: "Table",
        rc_sizes: RCSizes,
        r: int,
        c: int,
    ) -> None:
        bw = table.style.w
        bh = table.style.h
        w = sum(rc_sizes.cols[c:c + self.span.x]) + bw
        h = sum(rc_sizes.rows[r:r + self.span.y]) + 1
        x = sum(rc_sizes.cols[:c])
        y = sum(rc_sizes.rows[:r])
        p = Grid.full((w, h), " ")
        b = Grid.full((w, h), _Con.N)
        if self.border.t:
            b[1:-1, 0] |= Grid.full((w - 2, 1), _Con.L | _Con.R)
            b.data[0][0] |= _Con.R
            b.data[-1][0] |= _Con.L
        if self.border.b:
            b[1:-1, -1] |= Grid.full((w - 2, 1), _Con.L | _Con.R)
            b.data[0][-1] |= _Con.R
            b.data[-1][-1] |= _Con.L
        if self.border.l:
            b[:bw, 1:-1] |= Grid.full((bw, h - 2), _Con.U | _Con.D)
            b[:bw, 0] |= Grid.full((bw, 1), _Con.D)
            b[:bw, -1] |= Grid.full((bw, 1), _Con.U)
        if self.border.r:
            b[-bw:, 1:-1] |= Grid.full((bw, h - 2), _Con.U | _Con.D)
            b[-bw:, 0] |= Grid.full((bw, 1), _Con.D)
            b[-bw:, -1] |= Grid.full((bw, 1), _Con.U)
        v = Grid.from_str(self.value)
        p[self.padding.l + bw, self.padding.t + 1] = v
        grid[x, y] = p
        b_grid[x:x + b.width, y:y + b.height] |= b


_cel = Cel | None


class Row(UserList[_cel]):

    def __init__(
        self,
        *data: _cel,
    ) -> None:
        super().__init__(data)

    def get_min_size(self, table: "Table") -> Point:
        w, h = 0, 0
        for cel in self:
            if cel == None: continue
            cw, ch = cel.get_min_size(table)
            w, h = max(w, cw), max(h, ch)
        return Point(w, h)

    def draw(
        self,
        grid: Grid[str],
        b_grid: Grid[_Con],
        table: "Table",
        rc_sizes: RCSizes,
        r: int,
    ) -> None:
        c = 0
        for cel in self:
            if cel == None:
                c += 1
                continue
            cel.draw(grid, b_grid, table, rc_sizes, r, c)
            c += cel.span.x
        pass


_row = Row | list[_cel] | None


class Table(UserList[Row | None]):

    def __init__(
        self,
        *data: _row,
        style: TableStyle = BOX_STYLE,
    ) -> None:
        rows: list[Row | None] = []
        for row in data:
            if isinstance(row, (Row, type(None))):
                rows.append(row)
            else:
                rows.append(Row(*row))
        super().__init__(rows)
        self.style = style

    @property
    def size(self) -> Point:
        w, h = 0, len(self)
        for r, row in enumerate(reversed(self)):
            if row == None: continue
            rw = 0
            for col in row:
                if col == None:
                    rw += 1
                    continue
                rw += col.span.x
                if col.span.y > (r + 1):
                    h += col.span.y - (r + 1)
            w = max(w, rw)
        return Point(w, h)

    def get_rc_sizes(self) -> RCSizes:
        w, h = self.size
        row_sizes, col_sizes = [0] * h, [0] * w
        for r, row in enumerate(self):
            if not isinstance(row, Row):
                continue
            c = 0
            for cel in row:
                if cel == None:
                    c += 1
                    continue
                size = cel.get_min_size(self)
                x_mod = size.x % cel.span.x
                y_mod = size.y % cel.span.y
                for x in range(cel.span.x):
                    x_rem = x_mod if x == 0 else 0
                    for y in range(cel.span.y):
                        y_rem = y_mod if y == 0 else 0
                        row_sizes[r + y] = max(row_sizes[r + y],
                                               size.y // cel.span.y + y_rem)
                        col_sizes[c + x] = max(col_sizes[c + x],
                                               size.x // cel.span.x + x_rem)
                c += cel.span.x
        return RCSizes(row_sizes, col_sizes)

    def fill_borders(self, grid: Grid[str], b_grid: Grid[_Con]) -> None:
        for x, col in enumerate(grid.data):
            for y in range(len(col)):
                con = b_grid.data[x][y]
                if con == (_Con.R | _Con.L | _Con.U | _Con.D):
                    grid.data[x][y] = self.style.rlud
                    continue
                if con == (_Con.R | _Con.L | _Con.D):
                    grid.data[x][y] = self.style.rld
                    continue
                if con == (_Con.R | _Con.U | _Con.D):
                    grid.data[x][y] = self.style.rud
                    continue
                if con == (_Con.L | _Con.U | _Con.D):
                    grid.data[x][y] = self.style.lud
                    continue
                if con == (_Con.R | _Con.L | _Con.U):
                    grid.data[x][y] = self.style.rlu
                    continue
                if con == (_Con.U | _Con.D):
                    grid.data[x][y] = self.style.ud
                    continue
                if con == (_Con.R | _Con.L):
                    grid.data[x][y] = self.style.rl
                    continue
                if con == (_Con.R | _Con.D):
                    grid.data[x][y] = self.style.rd
                    continue
                if con == (_Con.L | _Con.D):
                    grid.data[x][y] = self.style.ld
                    continue
                if con == (_Con.R | _Con.U):
                    grid.data[x][y] = self.style.ru
                    continue
                if con == (_Con.L | _Con.U):
                    grid.data[x][y] = self.style.lu
                    continue
                if con > 0:
                    grid.data[x][y] = str(con.value)

    def render(self) -> Grid[str]:
        grid = Grid[str]()
        b_grid = Grid[_Con]()
        rc_sizes = self.get_rc_sizes()
        width, height = sum(rc_sizes.cols), sum(rc_sizes.rows)
        grid.resize((width + self.style.w, height + self.style.h), " ")
        b_grid.resize((width + self.style.w, height + self.style.h), _Con.N)
        for r, row in enumerate(self):
            if row == None: continue
            row.draw(grid, b_grid, self, rc_sizes, r)

        self.fill_borders(grid, b_grid)
        return grid


if __name__ == "__main__":
    child = Table(
        Row(
            Cel("AAAA\nAAAA"),
            Cel("BBBB\nBBBB"),
            Cel("CCCC\nCCCC"),
        ), )

    grid = Table(
        Row(
            Cel("F\nY\nS\nT", span=(1, 3)),
            Cel("Format", span=(2, 1), border=False),
            Cel("You"),
        ),
        Row(
            None,
            Cel("Some", span=(1, 2), border=(False, True, False, True)),
            Cel("Tables", span=(3, 1)),
        ),
        Row(
            None,
            None,
            Cel("for\nreal", border=(False, True, True, True)),
            Cel("good\ntimes", span=(1, 3)),
        ),
        Row(Cel(str(child.render()), span=(2,1)),),
        style=DBL_VERT_BOX_STYLE,
    )

    print(grid.render())
