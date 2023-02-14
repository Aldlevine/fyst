```
┌─────┐ ┌──────────────────────────────────────────────┐
│     │ │            Format You Some Tables            │
│     │ ├───────────┬───────────┬───────────┬──────────┤
│     │ │     F     │     Y     │     S     │    T     │
│     │ ├───────────┴───────────┴───────────┴──────────┤
│     │ │  Format        You        Some       Tables  │
│     │ └──────────────────────────────────────────────┘
│  F  │ ┌──────────────────────────────────────────────┐
│  Y  │ │                   Supports                   │
│  S  │ ├───────────────────────┬──────────────────────┤
│  T  │ │  -------------------  │ -------------------  │
│     │ │    Row / Col spans    │    Nested tables     │
│     │ │  -------------------  │ -------------------  │
│     │ │    V / H alignment    │  Cascading styles    │
│     │ │  -------------------  │ -------------------  │
│     │ │     Border styles     │      Type safe       │
│     │ │  -------------------  │ -------------------  │
└─────┘ └───────────────────────┴──────────────────────┘
```

## What is it?

A table formatter that takes "inspiration" from the standard HTML `<table>`.

## Usage

### A basic example
*See example.py for additional examples.*

```python
from fyst import Cel, Row, Table

t = Table(
    Row(
        None,
        Cel("Format You Some Tables", span=(4, 1)),
        border=0,
        padding=(0, 1),
    ),
    [None, "F"     , "Y"     , "S"     , "T"     ],
    ["F",  "Format", "You"   , "Some"  , "Tables"],
    ["Y",  "You"   , "Some"  , "Tables", "Format"],
    ["S",  "Some"  , "Tables", "Format", "You"   ],
    ["T",  "Tables", "Format", "You"   , "Some"  ],
    padding=(1, 0),
    halign="middle",
)

print(t)

"""
           Format You Some Tables        
    ┌────────┬────────┬────────┬────────┐
    │   F    │   Y    │   S    │   T    │
┌───┼────────┼────────┼────────┼────────┤
│ F │ Format │  You   │  Some  │ Tables │
├───┼────────┼────────┼────────┼────────┤
│ Y │  You   │  Some  │ Tables │ Format │
├───┼────────┼────────┼────────┼────────┤
│ S │  Some  │ Tables │ Format │  You   │
├───┼────────┼────────┼────────┼────────┤
│ T │ Tables │ Format │  You   │  Some  │
└───┴────────┴────────┴────────┴────────┘
"""
```

### Details

Similar to it's HTML counterpart, a `Table` is a list of `Row`s which are in turn a list of `Cel`s. To support terse usage, `Row` and `Col` can be elided in favor of `list` and `Any` respectively.

Styles are cascaded downwards. E.g. the style properties set on the `Table`, will be automatically applied to child `Row`s / `Cel`s, unless the child overrides that property.

Style properties include:
- padding: `int | tuple[int, int] | tuple[int, int, int, int]`
    - The padding applied around the content of the `Cel`
    - the items are in order of: left, top, right, bottom (l, t, r, b)
- border: `int | tuple[int, int] | tuple[int, int, int, int]`
    - Whether or not to apply a border to each edge of the `Cel`
    - Currently only supports `Literal[0] | Literal[1]`. Future versions may support higher values for thicker borders.
- halign: `"left" | "middle" | "right"`
    - The horizontal alignment of the content in the `Cel`
- valign: `"top" | "middle" | "bottom"`
    - The vertical alignment of the content in the `Cel`

## Under the hood

A large part of what powers `fyst` is `fyst.grid.Grid[T]`.

`Grid` is a typesafe 2D matrix that supports NumPy like slicing semantics, as well as some basic level broadcasting.

Why? Because we didn't want to introduce dependencies into the package. It's possible we may experiment with a NumPy based optional back-end if it can provide a performance improvement.