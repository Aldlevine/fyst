from dataclasses import dataclass as _dataclass
from typing import Generic as _Generic
from typing import Literal as _Literal
from typing import NamedTuple as _NamedTuple
from typing import Optional as _Optional
from typing import TypedDict as _TypedDict
from typing import TypeVar as _TypeVar

from typing_extensions import NotRequired as _NotRequired

V = _TypeVar("V")


class _Edges(_Generic[V]):

    def __init__(
        self,
        *v: V,
    ) -> None:
        super().__init__()
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


_EdgesArg = _Edges[V] | tuple[V, V, V, V] | tuple[V, V] | V


class Padding(_Edges[int]):
    pass


PaddingArg = Padding | tuple[int, int, int, int] | tuple[int, int] | int


class Border(_Edges[bool]):
    pass


BorderArg = Border | tuple[bool, bool, bool, bool] | tuple[bool, bool] | bool

Valign = _Literal["top"] | _Literal["middle"] | _Literal["bottom"]
Halign = _Literal["left"] | _Literal["middle"] | _Literal["right"]


class StyleArg(_TypedDict):
    padding: _NotRequired[PaddingArg]
    border: _NotRequired[BorderArg]
    halign: _NotRequired[Halign]
    valign: _NotRequired[Valign]


class StyleOpt(_TypedDict):
    padding: _Optional[Padding]
    border: _Optional[Border]
    halign: _Optional[Halign]
    valign: _Optional[Valign]


class Style(_NamedTuple):
    padding: Padding
    border: Border
    halign: Halign
    valign: Valign


def style_from_style_arg(style_arg: StyleArg) -> StyleOpt:
    padding = style_arg["padding"] if "padding" in style_arg else None
    border = style_arg["border"] if "border" in style_arg else None
    halign = style_arg["halign"] if "halign" in style_arg else None
    valign = style_arg["valign"] if "valign" in style_arg else None

    if isinstance(padding, Padding):
        padding = padding
    elif isinstance(padding, tuple):
        padding = Padding(*padding)
    elif isinstance(padding, int):
        padding = Padding(padding)

    if isinstance(border, Border):
        border = border
    elif isinstance(border, tuple):
        border = Border(*border)
    elif isinstance(border, int):
        border = Border(border)

    return StyleOpt(
        padding=padding,
        border=border,
        halign=halign,
        valign=valign,
    )


@_dataclass
class BorderStyle:
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


BASIC_STYLE = BorderStyle(
    w=1,
    h=1,
    ud="|",
    rl="-",
    rd="+",
    rld="+",
    ld="+",
    rud="+",
    rlud="+",
    lud="+",
    ru="+",
    rlu="+",
    lu="+",
)
"""`BorderStyle` using `|`, `-`, and `+` characters"""

BOX_STYLE = BorderStyle(
    w=1,
    h=1,
    ud="│",
    rl="─",
    rd="┌",
    rld="┬",
    ld="┐",
    rud="├",
    rlud="┼",
    lud="┤",
    ru="└",
    rlu="┴",
    lu="┘",
)
"""`BorderStyle` using unicode box characters."""