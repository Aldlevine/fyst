from __future__ import annotations as _annotations

from collections import UserList as _UserList
from enum import IntFlag as _IntFlag
from typing import Any as _Any
from typing import NamedTuple as _NamedTuple

from typing_extensions import Unpack as _Unpack

from .grid import Grid as _Grid
from .grid import Point as _Point
from .grid import PointArg as _PointArg
from .style import BOX_STYLE as _BOX_STYLE
from .style import Border as _Border
from .style import BorderStyle as _BorderStyle
from .style import Padding as _Padding
from .style import Style as _Style
from .style import StyleArg as _StyleArg
from .style import style_from_style_arg as _style_from_style_arg


class _RCSizes(_NamedTuple):
    rows: list[int]
    cols: list[int]


class _Con(_IntFlag):
    N = 0
    L = 1
    U = 2
    R = 4
    D = 8


def _halign_middle(s: str) -> str:
    lines = s.split("\n")
    width = max([len(l) for l in lines])
    return "\n".join([l.center(width) for l in lines])


def _halign_right(s: str) -> str:
    lines = s.split("\n")
    width = max([len(l) for l in lines])
    return "\n".join([l.rjust(width) for l in lines])


def _divvy(size: int, sizes: list[int]) -> list[int]:
    if (len(sizes) == 0):
        return []
    size = max(size - sum(sizes), 0)
    mod = size % len(sizes)
    div = size // len(sizes)
    return [sizes[i] + div + max(mod - i, 0) for i in range(len(sizes))]


class Cel:
    """Represents a single cell within a table
    """

    def __init__(
            self,
            value: _Any = "",
            span: _PointArg = (1, 1),
            **style: _Unpack[_StyleArg],
    ) -> None:
        """
        Args:
            value: The value displayed by the cel. Will be converted to a string with `str()`.
            span: The number of cols/rows the cel spans.
        
        Keyword Args:
            padding (padding_): The amount of interior padding applied to each side (l, t, r, b)
            border (border_): Whether to display the border on each side (l, t, r, b)
            halign (halign_): The horizontal alignment of the content
            valign (valign_): The vertical alignment of the content
        """
        super().__init__()
        self.value = value
        """The value the cell will display"""
        self.span = _Point(*span)
        """The number of (cols, rows) the cell spans"""
        self.style = _style_from_style_arg(style)
        """The style used to render the cell. Each property will cascade from the parent when `None`"""

    def cascade_style(self, table: Table, row: Row) -> None:
        style = self.style
        for k in style:
            v = style[k]  # type: ignore
            if v == None:
                v = row.style[k]  # type: ignore
            if v == None:
                v = table.style[k]  # type: ignore
            style[k] = v

        self.cascaded_style = _Style(**style)  # type: ignore

    def get_min_size(self, table: Table, row: Row) -> _Point:
        bw = table.border_style.w
        bh = table.border_style.h
        s = str(self.value)
        lines = s.split("\n")
        w, h = 0, len(lines)
        for l in lines:
            w = max(len(l), w)
        return _Point(
            w + self.cascaded_style.padding.l + self.cascaded_style.padding.r +
            int(self.cascaded_style.border.l or self.cascaded_style.border.r) *
            bw,
            h + self.cascaded_style.padding.t + self.cascaded_style.padding.b +
            int(self.cascaded_style.border.t or self.cascaded_style.border.b) *
            bh,
        )

    def render(
        self,
        grid: _Grid[str],
        b_grid: _Grid[_Con],
        table: Table,
    ) -> None:
        bw = table.border_style.w
        bh = table.border_style.h
        if bh > 0:
            if self.cascaded_style.border.t:
                if b_grid.width > 2:
                    b_grid[1:-1, :bh] |= _Con.L | _Con.R
                b_grid[0, :bh] |= _Con.R
                b_grid[-1, :bh] |= _Con.L
            if self.cascaded_style.border.b:
                if b_grid.width > 2:
                    b_grid[1:-1, -bh:] |= _Con.L | _Con.R
                b_grid[0, -bh:] |= _Con.R
                b_grid[-1, -bh:] |= _Con.L
        if bw > 0:
            if self.cascaded_style.border.l:
                if b_grid.height > 2:
                    b_grid[:bw, 1:-1] |= _Con.U | _Con.D
                b_grid[:bw, 0] |= _Con.D
                b_grid[:bw, -1] |= _Con.U
            if self.cascaded_style.border.r:
                if b_grid.height > 2:
                    b_grid[-bw:, 1:-1] |= _Con.U | _Con.D
                b_grid[-bw:, 0] |= _Con.D
                b_grid[-bw:, -1] |= _Con.U

        s = str(self.value)
        if self.cascaded_style.halign == "middle":
            s = _halign_middle(s)
        elif self.cascaded_style.halign == "right":
            s = _halign_right(s)
        v = _Grid.from_str(s)

        x, y = 0, 0
        if self.cascaded_style.halign == "left":
            x = self.cascaded_style.padding.l + bw
        elif self.cascaded_style.halign == "middle":
            x = (grid.width - v.width) // 2
        elif self.cascaded_style.halign == "right":
            x = grid.width - v.width - self.cascaded_style.padding.r - bw

        if self.cascaded_style.valign == "top":
            y = self.cascaded_style.padding.t + bh
        elif self.cascaded_style.valign == "middle":
            y = (grid.height - v.height) // 2
        elif self.cascaded_style.valign == "bottom":
            y = grid.height - v.height - self.cascaded_style.padding.b - bh

        grid[x, y] = v


_cel = _Any


class Row(_UserList[_cel]):

    def __init__(
        self,
        *data: _cel,
        **style: _Unpack[_StyleArg],
    ) -> None:
        cels = [
            c if isinstance(c, Cel) else
            Cel(padding=0, border=False) if c is None else Cel(c) for c in data
        ]
        super().__init__(cels)
        self.style = _style_from_style_arg(style)

    def render(
        self,
        grid: _Grid[str],
        b_grid: _Grid[_Con],
        table: Table,
        rc_sizes: _RCSizes,
        r: int,
    ) -> None:
        bw = table.border_style.w
        bh = table.border_style.h
        c = 0
        for cel in self:
            if not isinstance(cel, Cel):
                c += 1
                continue
            w = sum(rc_sizes.cols[c:c + cel.span.x]) + bw
            h = sum(rc_sizes.rows[r:r + cel.span.y]) + bh
            x = sum(rc_sizes.cols[:c])
            y = sum(rc_sizes.rows[:r])
            cel.render(grid[x:x + w, y:y + h], b_grid[x:x + w, y:y + h], table)
            c += cel.span.x


_row = Row | list[_cel] | None


class Table(_UserList[Row]):

    def __init__(
        self,
        *data: _row,
        border_style: _BorderStyle = _BOX_STYLE,
        **style: _Unpack[_StyleArg],
    ) -> None:
        rows: list[Row] = []
        for row in data:
            if row is None:
                rows.append(Row())
            elif isinstance(row, (Row)):
                rows.append(row)
            else:
                rows.append(Row(*row))
        super().__init__(rows)
        self.border_style = border_style

        self.style = _style_from_style_arg(style)
        self.style["border"] = self.style["border"] or _Border(True)
        self.style["padding"]  = self.style["padding"] or _Padding(3, 0)
        self.style["halign"] = self.style["halign"] or "left"
        self.style["valign"] = self.style["valign"] or "top"

    @property
    def size(self) -> _Point:
        w, h = 0, len(self)
        for r, row in enumerate(reversed(self)):
            rw = 0
            for col in row:
                if col == None:
                    rw += 1
                    continue
                rw += col.span.x
                if col.span.y > (r + 1):
                    h += col.span.y - (r + 1)
            w = max(w, rw)
        return _Point(w, h)

    @property
    def grid(self) -> _Grid[str]:
        if not hasattr(self, "_grid"):
            self._grid = self._render()
        return self._grid

    def _render(self) -> _Grid[str]:
        self._cascade_styles()
        grid = _Grid[str]()
        b_grid = _Grid[_Con]()
        rc_sizes = self._get_rc_sizes()
        width, height = sum(rc_sizes.cols), sum(rc_sizes.rows)
        grid = _Grid.full(
            (width + self.border_style.w, height + self.border_style.h),
            " ",
        )
        b_grid = _Grid.full(
            (width + self.border_style.w, height + self.border_style.h),
            _Con.N,
        )
        for r, row in enumerate(self):
            row.render(grid, b_grid, self, rc_sizes, r)

        self._fill_borders(grid, b_grid)
        return grid

    def _get_rc_sizes(self) -> _RCSizes:
        w, h = self.size
        row_sizes, col_sizes = [0] * h, [0] * w
        cels = [(r, c, row, cel) for r, row in enumerate(self)
                for c, cel in enumerate(row) if isinstance(cel, Cel)]

        cels.sort(key=lambda t: t[3].span)
        for r, c, row, cel in cels:
            size = cel.get_min_size(self, row)
            if cel.span.x > 0:
                col_sizes[c:c + cel.span.x] = _divvy(
                    size.x, col_sizes[c:c + cel.span.x])
            if cel.span.y > 0:
                row_sizes[r:r + cel.span.y] = _divvy(
                    size.y, row_sizes[r:r + cel.span.y])
        return _RCSizes(row_sizes, col_sizes)

    def _fill_borders(self, grid: _Grid[str], b_grid: _Grid[_Con]) -> None:
        for x in range(grid.width):
            for y in range(grid.height):
                con = b_grid[x, y].item()
                if con == (_Con.R | _Con.L | _Con.U | _Con.D):
                    grid[x, y] = self.border_style.rlud
                    continue
                if con == (_Con.R | _Con.L | _Con.D):
                    grid[x, y] = self.border_style.rld
                    continue
                if con == (_Con.R | _Con.U | _Con.D):
                    grid[x, y] = self.border_style.rud
                    continue
                if con == (_Con.L | _Con.U | _Con.D):
                    grid[x, y] = self.border_style.lud
                    continue
                if con == (_Con.R | _Con.L | _Con.U):
                    grid[x, y] = self.border_style.rlu
                    continue
                if con == (_Con.U | _Con.D):
                    grid[x, y] = self.border_style.ud
                    continue
                if con == (_Con.R | _Con.L):
                    grid[x, y] = self.border_style.rl
                    continue
                if con == (_Con.R | _Con.D):
                    grid[x, y] = self.border_style.rd
                    continue
                if con == (_Con.L | _Con.D):
                    grid[x, y] = self.border_style.ld
                    continue
                if con == (_Con.R | _Con.U):
                    grid[x, y] = self.border_style.ru
                    continue
                if con == (_Con.L | _Con.U):
                    grid[x, y] = self.border_style.lu
                    continue
                if con & (_Con.R | _Con.L):
                    grid[x, y] = self.border_style.rl
                    continue
                if con & (_Con.U | _Con.D):
                    grid[x, y] = self.border_style.ud
                    continue
                if con > 0:
                    grid[x, y] = str(con.value)

    def _cascade_styles(self) -> None:
        for row in self:
            for cel in row:
                if not isinstance(cel, Cel): continue
                cel.cascade_style(self, row)

    def __str__(self) -> str:
        return str(self.grid)
