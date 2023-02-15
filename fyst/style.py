from __future__ import annotations as _annotations

from dataclasses import dataclass as _dataclass
from typing import Any as _Any
from typing import Generic as _Generic
from typing import Literal as _Literal
from typing import NamedTuple as _NamedTuple
from typing import Optional as _Optional
from typing import TypedDict as _TypedDict
from typing import TypeVar as _TypeVar

from typing_extensions import NotRequired as _NotRequired

from .color import Color as _Color

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


_PaddingArg = Padding | tuple[int, int, int, int] | tuple[int, int] | int

_border = _Literal[0] | _Literal[1]


class Border(_Edges[_border]):
    pass


_BorderArg = Border | tuple[_border, _border, _border,
                            _border] | tuple[_border, _border] | _border

Valign = _Literal["top"] | _Literal["middle"] | _Literal["bottom"]
Halign = _Literal["left"] | _Literal["middle"] | _Literal["right"]

ColorArg = _Color | int | tuple[int, int, int]

class StyleArg(_TypedDict):
    padding: _NotRequired[_PaddingArg]
    border: _NotRequired[_BorderArg]
    halign: _NotRequired[Halign]
    valign: _NotRequired[Valign]
    fg: _NotRequired[ColorArg]
    bg: _NotRequired[ColorArg]
    border_fg: _NotRequired[ColorArg]
    border_bg: _NotRequired[ColorArg]


class StyleOpt(_TypedDict):
    padding: _Optional[Padding]
    border: _Optional[Border]
    halign: _Optional[Halign]
    valign: _Optional[Valign]
    fg: _Optional[_Color]
    bg: _Optional[_Color]
    border_fg: _Optional[_Color]
    border_bg: _Optional[_Color]


class Style(_NamedTuple):
    padding: Padding
    border: Border
    halign: Halign
    valign: Valign
    fg: _Color
    bg: _Color
    border_fg: _Color
    border_bg: _Color


class Stylable:

    def __init__(
        self,
        style: StyleArg,
        *args: _Any,
        **kwargs: _Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.padding = style["padding"] if "padding" in style else None
        self.border = style["border"] if "border" in style else None
        self.halign = style["halign"] if "halign" in style else None
        """The element's halign
        """
        self.valign = style["valign"] if "valign" in style else None
        """The element's valign
        """
        self.fg = style["fg"] if "fg" in style else None
        self.bg = style["bg"] if "bg" in style else None
        self.border_fg = style["border_fg"] if "border_fg" in style else None
        self.border_bg = style["border_bg"] if "border_bg" in style else None

    def _cascade_style(self, *parents: Stylable) -> None:
        style = {f: getattr(self, f) for f in Style._fields}
        for k in Style._fields:
            v = style[k]
            for p in parents:
                if v != None:
                    break
                v = getattr(p, k)
            style[k] = v

        self.cascaded_style = Style(**style)

    @property
    def padding(self) -> _Optional[Padding]:
        return self._padding

    @padding.setter
    def padding(self, padding: _Optional[_PaddingArg]) -> None:
        """The element's padding
        """
        if isinstance(padding, (Padding, type(None))):
            padding = padding
        elif isinstance(padding, tuple):
            padding = Padding(*padding)
        else:
            padding = Padding(padding)
        self._padding = padding

    @property
    def border(self) -> _Optional[Border]:
        return self._border

    @border.setter
    def border(self, border: _Optional[_BorderArg]) -> None:
        if isinstance(border, Border):
            border = border
        elif isinstance(border, tuple):
            border = Border(*border)
        elif isinstance(border, int):
            border = Border(border)
        self._border = border

    @property
    def fg(self) -> _Optional[_Color]:
        return self._fg

    @fg.setter
    def fg(self, v: _Optional[ColorArg]) -> None:
        self._fg = _Color(v) if v is not None else None

    @property
    def bg(self) -> _Optional[_Color]:
        return self._bg

    @bg.setter
    def bg(self, v: _Optional[ColorArg]) -> None:
        self._bg = _Color(v) if v is not None else None

    @property
    def border_fg(self) -> _Optional[_Color]:
        return self._border_fg

    @border_fg.setter
    def border_fg(self, v: _Optional[ColorArg]) -> None:
        self._border_fg = _Color(v) if v is not None else None

    @property
    def border_bg(self) -> _Optional[_Color]:
        return self._border_bg

    @border_bg.setter
    def border_bg(self, v: _Optional[ColorArg]) -> None:
        self._border_bg = _Color(v) if v is not None else None



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