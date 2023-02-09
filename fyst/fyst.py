from collections import UserList
from dataclasses import dataclass
from typing import Any, Iterable


class Col():
    """
    --------
    Defines a column within a `Row`

    Attributes:
        value: The value to display
        span: How many columns to span
        align: Horizontal alignment - `default` | `center` | `left` | `right`
    """

    def __init__(self, value: Any, span: int = 1, align: str = "default") -> None:
        self.value = value
        self.span = span
        self.align = align

    def min_width(self) -> int:
        return len(self.render(0, [], "test"))

    def render(self, width: int, col_widths: list[int], align: str) -> str:
        if align == "test":
            return f"""{self.value!s}"""

        align = align if self.align == "default" else self.align
        match align:
            case "center":
                return f"""{self.value!s:^{width}}"""
            case "right":
                return f"""{self.value!s:>{width}}"""
            case "left" | _:
                return f"""{self.value!s:<{width}}"""


class Row(UserList[Col]):
    """
    --------
    Defines a row within a `Table`

    Attrs:
        data: `Col`s in the row
        align: Horizontal alignment - `default` | `center` | `left` | `right`
    """

    def __init__(self, *data: Col, align: str = "default") -> None:
        super().__init__(data)
        self.align = align

    def render(self, idx: int, table: "Table", col_widths: list[int], align: str) -> str:
        align = align if self.align == "default" else self.align
        r = table.style.v
        col_idx = 0
        for col in self:
            col_width = sum(
                col_widths[col_idx:col_idx + col.span]) + ((col.span - 1) * (len(table.style.v) + 2))
            r += " " + col.render(col_width, col_widths, align) + " " + table.style.v
            col_idx += col.span
        return r

class Blank(Row):
    """
    --------
    Defines a blank row.
    Like `Sep` but creates a bordered gap between sections.
    """

    def __init__(self) -> None:
        super().__init__()

    def render(self, idx: int, table: "Table", col_widths: list[int], align: str) -> str:
        return ""

class Sep(Row):
    """
    --------
    Defines a separator row.
    """

    def __init__(self) -> None:
        super().__init__()

    def render(self, idx: int, table: "Table", col_widths: list[int], align: str) -> str:
        prev_row: Iterable[Col] = table[idx-1] if idx-1 > 0 else []
        next_row: Iterable[Col] = table[idx+1] if idx+1 < len(table) else []
        prev_col_indices: dict[int, bool] = {
            i: False for i in range(len(col_widths))}
        next_col_indices: dict[int, bool] = {
            i: False for i in range(len(col_widths))}
        prev_idx = 0
        next_idx = 0
        for col in prev_row:
            prev_col_indices[prev_idx] = True
            prev_idx += col.span
        for col in next_row:
            next_col_indices[next_idx] = True
            next_idx += col.span

        inner = ""
        for i, col in enumerate(col_widths):
            inner += table.style.h * (col + 2)
            if i < len(col_widths) - 1:
                if prev_col_indices[i + 1] and next_col_indices[i + 1]:
                    inner += table.style.rlud
                elif prev_col_indices[i + 1]:
                    inner += table.style.rlu
                elif next_col_indices[i + 1]:
                    inner += table.style.rld
                else:
                    inner += table.style.h * len(table.style.v)

        if idx == 0 or isinstance(prev_row, Blank):
            left_end = table.style.rd
            right_end = table.style.ld
        elif idx == len(table) - 1 or isinstance(next_row, Blank):
            left_end = table.style.ru
            right_end = table.style.lu
        else:
            left_end = table.style.rud
            right_end = table.style.lud

        return left_end + inner + right_end

@dataclass
class TableStyle:
    """
    --------
    A datatype used to define a table style.
    """

    v: str
    h: str
    rd: str
    rld: str
    ld: str
    rud: str
    rlud: str
    lud: str
    ru: str
    rlu: str
    lu: str

BASIC_STYLE = TableStyle(
    v = "|", h = "-",
    rd  = "+" , rld  = "+" , ld  = "+",
    rud = "+" , rlud = "+" , lud = "+",
    ru  = "+" , rlu  = "+" , lu  = "+",
)
"""`TableStyle` using `|`, `-`, and `+` characters"""

BOX_STYLE = TableStyle(
    v   = "│" , h    = "─",
    rd  = "┌" , rld  = "┬" , ld  = "┐",
    rud = "├" , rlud = "┼" , lud = "┤",
    ru  = "└" , rlu  = "┴" , lu  = "┘",
)
"""`TableStyle` using unicode box characters."""

DBL_VERT_BOX_STYLE = TableStyle(
    v   = "││" , h    = "─",
    rd  = "┌┬" , rld  = "┬┬" , ld  = "┬┐",
    rud = "├┼" , rlud = "┼┼" , lud = "┼┤",
    ru  = "└┴" , rlu  = "┴┴" , lu  = "┴┘",
)
"""`TableStyle` using unicode box characters, but with doubled verticals."""

class Table(UserList[Row]):
    """
    --------
    Defines a table

    Attrs:
        data: `Row`s in the table
        align: Horizontal alignment - `default` | `center` | `left` | `right`
        style: The style used to render the table
    """

    def __init__(
        self,
        *data: Row,
        align: str = "left",
        style: TableStyle = BOX_STYLE,
    ) -> None:
        super().__init__(data)
        self.align = align
        self.style = style

    def __repr__(self) -> str:
        col_widths = self._get_col_widths()
        rows = "\n".join([
            row.render(i, self, col_widths, self.align) for i, row in enumerate(self) if not isinstance(row, Blank)
        ])
        return rows

    def _get_col_widths(self) -> list[int]:
        col_widths: list[int] = []
        for row in self:
            col_idx = 0
            for col in row:
                min_width = col.min_width()
                split_width = min_width // col.span
                rem_width = min_width % col.span
                for sp in range(col.span):
                    while len(col_widths) < col_idx + sp + 1:
                        col_widths.append(0)
                    rem = rem_width if sp < col.span else 0
                    col_widths[col_idx + sp] = max(col_widths[col_idx], split_width + rem)
                col_idx += col.span
        return col_widths


if __name__ == "__main__":
    t = Table(
        Sep(),
        Row(Col("Format You Some Tables", span=4)),
        Sep(),
        Row(Col("F"), Col("Y"), Col("S"), Col("T")),
        Sep(),

        Blank(),

        Sep(),
        Row(Col("Format You", span=2), Col("Some"), Col("Tables")),
        Sep(),
        Row(Col("FYST", span=4)),
        Sep(),

        align = "center",
        style = DBL_VERT_BOX_STYLE,
    )

    print(t)

