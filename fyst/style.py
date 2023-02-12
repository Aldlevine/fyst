from dataclasses import dataclass


@dataclass
class TableStyle:
    """
    --------
    A datatype used to define a table style.

    Attrs:
        w: width of verticals
        h: height of horizontals
        ud: up/down `│`
        rl: right/left `─`
        rd: right/down `┌`
        rld: right/left/down `┬`
        ld: left/down `┐`
        rud: right/up/down `├`
        rlud: right/left/up/down `┼`
        lud: left/up/down `┤`
        ru: right/up `└`
        rlu: right/left/up `┴`
        lu: left/up `┘`
    """

    w: int
    h: int
    ud: str
    rl: str
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
    w = 1, h = 1,
    ud  = "|",  rl   = "-",
    rd  = "+" , rld  = "+" , ld  = "+",
    rud = "+" , rlud = "+" , lud = "+",
    ru  = "+" , rlu  = "+" , lu  = "+",
)
"""`TableStyle` using `|`, `-`, and `+` characters"""

BOX_STYLE = TableStyle(
    w = 1, h = 1,
    ud  = "│" , rl   = "─",
    rd  = "┌" , rld  = "┬" , ld  = "┐",
    rud = "├" , rlud = "┼" , lud = "┤",
    ru  = "└" , rlu  = "┴" , lu  = "┘",
)
"""`TableStyle` using unicode box characters."""

DBL_VERT_BOX_STYLE = TableStyle(
    w = 2, h = 1,
    ud  = "│" , rl   = "─",
    rd  = "┌" , rld  = "┬" , ld  = "┐",
    rud = "├" , rlud = "┼" , lud = "┤",
    ru  = "└" , rlu  = "┴" , lu  = "┘",
    # ud  = "││" , rl   = "─",
    # rd  = "┌┬" , rld  = "┬┬" , ld  = "┬┐",
    # rud = "├┼" , rlud = "┼┼" , lud = "┼┤",
    # ru  = "└┴" , rlu  = "┴┴" , lu  = "┴┘",
)
"""`TableStyle` using unicode box characters, but with doubled verticals."""
