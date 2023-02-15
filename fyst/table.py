from __future__ import annotations as _annotations

from collections import UserList as _UserList
from enum import IntFlag as _IntFlag
from typing import Any as _Any
from typing import NamedTuple as _NamedTuple

from typing_extensions import Unpack as _Unpack

from .color import RESET as _RESET
from .color import NoColor as _NoColor
from .color import delete_colors as _delete_colors
from .grid import Grid as _Grid
from .grid import Point as _Point
from .grid import PointArg as _PointArg
from .style import BOX_STYLE as _BOX_STYLE
from .style import Border as _Border
from .style import BorderStyle as _BorderStyle
from .style import Padding as _Padding
from .style import Stylable
from .style import StyleArg as _StyleArg


class _RCSizes(_NamedTuple):
    rows: list[int]
    cols: list[int]


class _Con(_IntFlag):
    N = 0
    L = 1
    U = 2
    R = 4
    D = 8


def _str_len(s: str) -> int:
    return len(_delete_colors(s))
    # return len(s)


def _halign_middle(s: str) -> str:
    lines = s.split("\n")
    width = max([_str_len(l) for l in lines])
    return "\n".join([l.center(width) for l in lines])


def _halign_right(s: str) -> str:
    lines = s.split("\n")
    width = max([_str_len(l) for l in lines])
    return "\n".join([l.rjust(width) for l in lines])


def _divvy(size: int, sizes: list[int]) -> list[int]:
    if (len(sizes) == 0):
        return []
    size = max(size - sum(sizes), 0)
    mod = size % len(sizes)
    div = size // len(sizes)
    return [sizes[i] + div + max(mod - i, 0) for i in range(len(sizes))]


class Cel(Stylable):
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
            padding (int, int*2, int*4): The amount of interior padding applied to each side (l, t, r, b)
            border (int, int*2, int*4): Whether to display the border on each side (l, t, r, b)
            halign ("left", "middle", "right"): The horizontal alignment of the content
            valign ("top", "middle", "bottom"): The vertical alignment of the content
        """
        super().__init__(style)
        self.value = value
        """The value the cell will display"""
        self.span = _Point(*span)
        """The number of (cols, rows) the cell spans"""

    def get_min_size(self, table: Table, row: Row) -> _Point:
        bw = table.border_style.w
        bh = table.border_style.h
        s = str(self.value)
        lines = s.split("\n")
        w, h = max([_str_len(l) for l in lines]), len(lines)
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
        c_grid: _Grid[str],
        table: Table,
    ) -> None:
        bw = table.border_style.w
        bh = table.border_style.h

        color: str = ""
        if self.cascaded_style.border_bg != _NoColor:
            color += format(self.cascaded_style.border_bg, "b")
        if self.cascaded_style.border_fg != _NoColor:
            color += format(self.cascaded_style.border_fg, "f")
        if bh > 0:
            if self.cascaded_style.border.t:
                if b_grid.width > 2:
                    b_grid[1:-1, :bh] |= _Con.L | _Con.R
                b_grid[0, :bh] |= _Con.R
                b_grid[-1, :bh] |= _Con.L
                if color != "":
                    c_grid[0, :bh] = color
                    c_grid[-2, :bh] = _RESET
            if self.cascaded_style.border.b:
                if b_grid.width > 2:
                    b_grid[1:-1, -bh:] |= _Con.L | _Con.R
                b_grid[0, -bh:] |= _Con.R
                b_grid[-1, -bh:] |= _Con.L
                if color != "":
                    c_grid[0, -bh:] = color
                    c_grid[-2, -bh:] = _RESET
        if bw > 0:
            if self.cascaded_style.border.l:
                if b_grid.height > 2:
                    b_grid[:bw, 1:-1] |= _Con.U | _Con.D
                b_grid[:bw, 0] |= _Con.D
                b_grid[:bw, -1] |= _Con.U
                if color != "":
                    c_grid[0, 1:-1] = color
                    c_grid[bw, 1:-1] = _RESET
            if self.cascaded_style.border.r:
                if b_grid.height > 2:
                    b_grid[-bw:, 1:-1] |= _Con.U | _Con.D
                b_grid[-bw:, 0] |= _Con.D
                b_grid[-bw:, -1] |= _Con.U
                if color != "":
                    c_grid[-bw - 1, :] = color
                    # c_grid[-1, :] += _RESET

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

        color: str = ""
        if self.cascaded_style.bg != _NoColor:
            color += format(self.cascaded_style.bg, "b")
        if self.cascaded_style.fg != _NoColor:
            color += format(self.cascaded_style.fg, "f")

        if color != "":
            c_grid[bw, bh:-bh] = _Grid.full((1, c_grid.height - bh * 2), color)
            c_grid[-bw, bh:-bh] = _Grid.full((1, c_grid.height - bh * 2),
                                             _RESET)
        # c_grid[-2, :] = _RESET
        # c_grid[1, -1] = _RESET
        # c_grid[1, 0] = _RESET

        grid[x, y] = v


_cel = _Any


class Row(Stylable, _UserList[Cel]):
    """Represents a single row within a table
    """

    def __init__(
        self,
        *data: _cel,
        **style: _Unpack[_StyleArg],
    ) -> None:
        """
        Args:
            data: The cells within this row
        
        Keyword Args:
            padding (int, int*2, int*4): The amount of interior padding applied to each side (l, t, r, b)
            border (int, int*2, int*4): Whether to display the border on each side (l, t, r, b)
            halign ("left", "middle", "right"): The horizontal alignment of the content
            valign ("top", "middle", "bottom"): The vertical alignment of the content
        """
        cels = [
            c if isinstance(c, Cel) else
            Cel(padding=0, border=0, fg=_NoColor, bg=_NoColor)
            if c is None else Cel(c) for c in data
        ]
        super().__init__(style, cels)

    def render(
        self,
        grid: _Grid[str],
        b_grid: _Grid[_Con],
        c_grid: _Grid[str],
        table: Table,
        rc_sizes: _RCSizes,
        r: int,
    ) -> None:
        bw = table.border_style.w
        bh = table.border_style.h
        c = 0
        for cel in self:
            w = sum(rc_sizes.cols[c:c + cel.span.x]) + bw
            h = sum(rc_sizes.rows[r:r + cel.span.y]) + bh
            x = sum(rc_sizes.cols[:c])
            y = sum(rc_sizes.rows[:r])
            cel.render(
                grid[x:x + w, y:y + h],
                b_grid[x:x + w, y:y + h],
                # one wider because of alternating columns
                c_grid[x:x + w + 1, y:y + h],
                table,
            )
            c += cel.span.x


_row = Row | list[_cel] | None


class Table(Stylable, _UserList[Row]):
    """Represents a table
    """

    def __init__(
        self,
        *data: _row,
        border_style: _BorderStyle = _BOX_STYLE,
        **style: _Unpack[_StyleArg],
    ) -> None:
        """
        Args:
            data: The rows within the table
            border_style: The set of characters used to draw borders
        
        Keyword Args:
            padding (int, int*2, int*4): The amount of interior padding applied to each side (l, t, r, b)
            border (int, int*2, int*4): Whether to display the border on each side (l, t, r, b)
            halign ("left", "middle", "right"): The horizontal alignment of the content
            valign ("top", "middle", "bottom"): The vertical alignment of the content
        """

        rows: list[Row] = []
        for row in data:
            if row is None:
                rows.append(Row())
            elif isinstance(row, (Row)):
                rows.append(row)
            else:
                rows.append(Row(*row))
        super().__init__(style, rows)
        self.border_style = border_style

        self.border = self.border or _Border(1)
        self.padding = self.padding or _Padding(3, 0)
        self.halign = self.halign or "left"
        self.valign = self.valign or "top"
        self.fg = self.fg or _NoColor
        self.bg = self.bg or _NoColor
        self.border_fg = self.border_fg or _NoColor
        self.border_bg = self.border_bg or _NoColor

    @property
    def size(self) -> _Point:
        """The size of the table in (cols, rows)
        """
        w, h = 0, len(self)
        for r, row in enumerate(reversed(self)):
            rw = 0
            for col in row:
                rw += col.span.x
                if col.span.y > (r + 1):
                    h += col.span.y - (r + 1)
            w = max(w, rw)
        return _Point(w, h)

    @property
    def grid(self) -> _Grid[str]:
        """The rendered grid
        """
        if not hasattr(self, "_grid"):
            self._grid = self._render()
        return self._grid

    def _render(self) -> _Grid[str]:
        self._cascade_styles()
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
        # 1 larger because each column in grid/b_grid is sandwiched between 2 columns in c_grid
        c_grid = _Grid.full(
            (width + self.border_style.w + 1, height + self.border_style.h),
            "",
        )
        for r, row in enumerate(self):
            row.render(grid, b_grid, c_grid, self, rc_sizes, r)

        self._fill_borders(grid, b_grid)
        grid[-1] = grid[-1] + _RESET
        return c_grid[:-1, :] + grid

    def _get_rc_sizes(self) -> _RCSizes:
        w, h = self.size
        row_sizes, col_sizes = [0] * h, [0] * w
        cels = [(r, c, row, cel) for r, row in enumerate(self)
                for c, cel in enumerate(row)]

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
                cel._cascade_style(row, self)

    def __str__(self) -> str:
        return str(self.grid)
