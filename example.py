from fyst import Cel, Row, Table
from fyst.color import NoColor, delete_colors
from fyst.grid import Grid
from fyst.style import BASIC_STYLE, BOX_STYLE



def table_example() -> Table:
    return Table(
        Row(
            None,
            Cel(
                "Format You Some Tables",
                span=(4, 1),
                bg=NoColor,
                fg=NoColor,
            ),
            border=0,
            padding=(0, 0, 0, 2),
        ),
        [None, "F", "Y", "S", "T"],
        ["F", "Format", "You", "Some", "Tables"],
        ["Y", "You", "Some", "Tables", "Format"],
        ["S", "Some", "Tables", "Format", "You"],
        ["T", "Tables", "Format", "You", "Some"],
        padding=(1, 0),
        halign="middle",
        bg=0x330000,
        border_bg=0x330000,
        fg=0x00ff00,
        border_fg=0x00ff00,
    )


def table_0() -> Table:
    st = Table(
        [Cel("Row / Col spans")],
        [Cel("V / H alignment")],
        [Cel("Border styles")],
        [Cel("Nested tables")],
        [Cel("Cascading styles")],
        [Cel("Type safe")],
        border_style=BASIC_STYLE,
        padding=(1, 0),
        border=(0, 1),
        halign="middle",
    )

    return Table(
        Row(
            Cel("F\nY\nS\nT", span=(1, 6)),
            Cel(padding=(1, 0), border=0, span=(1, 1)),
            Cel("Format You Some Tables", span=(4, 1)),
        ),
        Row(None, None, Cel("F"), Cel("Y"), Cel("S"), Cel("T")),
        Row(
            None,
            None,
            Cel("Format", border=(1, 1, 0, 1)),
            Cel("You"),
            Cel("Some"),
            Cel("Tables", border=(0, 1, 1, 1)),
            border=(0, 1),
        ),
        Row(None),
        Row(None, None, Cel("Supports", span=(4, 1))),
        Row(
            None,
            None,
            Cel(st.grid[:, 0:7], span=(2, 1), padding=0, valign="top"),
            Cel(st.grid[:, 6:], span=(2, 1)),
            valign="top",
        ),
        border_style=BOX_STYLE,
        halign="middle",
        valign="middle",
        padding=(2, 0),
        border=1,
    )


def table_1() -> Table:
    g = Grid[Cel].full((6, 4), Cel("World"))
    g[:, ::2] = Cel("Hello", border=0)
    g[::2, 1::2] = Cel("World", border=0, padding=(3, 0, 3, 1))
    return Table(*g.data)


def table_2() -> Table:
    return Table(
        [
            Table(
                ["A", "B"],
                ["C", "D"],
            ),
            Table(
                ["1", "2"],
                ["3", "4"],
            ),
        ],
        [
            Table(
                ["!", "@"],
                ["#", "$"],
            ),
            Table(
                [";", ":"],
                ["'", '"'],
            ),
        ],
        padding=(-1, 0, 2, 0),
        border=0,
    )


def table_3() -> Table:
    t = Table(*[[c for c in "ABCDEFG"]] * 4, )
    t.border = (0, 0, 0, 1)
    t[-1].border = 0
    for r in t:
        r[0].border = (0, 0, 1, 1)
    t[-1][0].border = (0, 0, 1, 0)
    return t


if __name__ == "__main__":
    print(table_0(), "\n")
    print(table_1(), "\n")
    print(table_2(), "\n")
    print(table_3(), "\n")
    print(table_example(), "\n")