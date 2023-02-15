from __future__ import annotations as _annotations

import os as _os
import re as _re
import sys as _sys
from dataclasses import dataclass as _dataclass
from typing import Optional as _Optional

if _sys.platform == "win32":
    _os.system("color")

_COLOR_TMPL = "\x1b[{};2;{};{};{}m"
_G_KEY = {"f": 38, "b": 48}
RESET = "\x1b[0m"

@_dataclass
class Color:
    r: int = 0
    g: int = 0
    b: int = 0

    def __init__(
        self,
        r: Color | int | tuple[int, int, int],
        g: _Optional[int] = None,
        b: _Optional[int] = None,
    ) -> None:
        if isinstance(r, Color):
            self.r = r.r
            self.g = r.g
            self.b = r.b
            return

        if isinstance(r, tuple):
            if g != None or b != None:
                raise TypeError
            self._init_rgb(*r)
            return

        if isinstance(g, int) and isinstance(b, int):
            self._init_rgb(r, g, b)
            return

        if g is None and b is None:
            self._init_hex(r)
            return

        raise TypeError

    def _init_rgb(self, r: int, g: int, b: int) -> None:
        self.r = r
        self.g = g
        self.b = b

    def _init_hex(self, hex: int) -> None:
        self.r = (hex & 0xff0000) >> 16
        self.g = (hex & 0x00ff00) >> 8
        self.b = (hex & 0x0000ff) >> 0

    def __format__(self, __format_spec: str) -> str:
        if __format_spec in ["f", "b"]:
            if self.r < 0 or self.g < 0 or self.b < 0:
                return ""
            return _COLOR_TMPL.format(
                _G_KEY[__format_spec],
                self.r,
                self.g,
                self.b,
            )
        return str(self)

NoColor = Color(-1, -1, -1)
# print(Color(128, 0, 0))
# print(f"""{Color(0xff6666):f}{Color(0x003333):b} Hello {_RESET}""")

def delete_colors(s: str) -> str:
    # ansi_escape = _re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    ansi_escape = _re.compile(r"\x1b\[\d+(;\d+)*m")
    return ansi_escape.sub("", s)
