from fyst import Cel, Row, Table
from fyst.grid import Grid
from fyst.style import BASIC_STYLE, BOX_STYLE, Border

if __name__ == "__main__":
    g = Grid[Cel].full((6, 4), Cel("World"))
    g[:, ::2] = Cel("Hello", border=False)
    g[::2, 1::2] = Cel("World", border=False, padding=(3, 0, 3, 1))
    print(Table(*g.data))

    print()

    st = Table(
        [Cel("Hello World")],
        [Cel("Goodnight Moon")],
        [Cel("Neato Frito")],
        border_style=BASIC_STYLE,
        padding=0,
        border=(False, True),
        halign="middle",
    )

    t = Table(
        Row(
            Cel("F\nY\nS\nT", span=(1, 6)),
            Cel(padding=(1, 0), border=False, span=(1, 1)),
            Cel("Format You Some Tables", span=(4, 1)),
        ),
        Row(None, None, Cel("F"), Cel("Y"), Cel("S"), Cel("T")),
        Row(None, None, Cel(""), padding=0, border=False),
        Row(
            None,
            None,
            Cel("Format", border=(True, True, False, True)),
            Cel("You"),
            Cel("Some"),
            Cel("Tables", border=(False, True, True, True)),
            border=(False, True),
        ),
        Row(
            None,
            None,
            Cel(st, span=(2, 2), padding=0, valign="top"),
            Cel("+ " * 8 + "+", span=(2, 1)),
        ),
        Row(None, None, None, None, Cel(st.grid[:, 2:], span=(2, 1))),
        border_style=BOX_STYLE,
        halign="middle",
        valign="middle",
        padding=(2, 0),
        border=True,
    )
    print(t)

    print(
        Table(
            [Table(["A", "B"], ["C", "D"]),
             Table(["1", "2"], ["3", "4"])],
            [Table(["!", "@"], ["#", "$"]),
             Table([";", ":"], ["'", '"'])],
            padding=(-1, 0, 2, 0),
            border=False,
        ))

    t = Table(
        *[[c for c in "ABCDEFG"]] * 4,
        border=(False, False, False, True),
    )
    t[-1].style["border"] = Border(False)

    print(t, "\n")