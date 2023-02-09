```
 ┌┬──────────────────────────────────────────┬┐
 ││          Format You Some Tables          ││
 ├┼─────────┬┬─────────┬┬─────────┬┬─────────┼┤
 ││    F    ││    Y    ││    S    ││    T    ││
 └┴─────────┴┴─────────┴┴─────────┴┴─────────┴┘
```

## What Is It?

A table formatter that takes "inspiration" from the standard HTML `<table>`.

## Usage

```python
from fyst import DBL_VERT_BOX_STYLE, Blank, Col, Row, Sep, Table

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

"""
┌┬──────────────────────────────────────────┬┐
││          Format You Some Tables          ││
├┼─────────┬┬─────────┬┬─────────┬┬─────────┼┤
││    F    ││    Y    ││    S    ││    T    ││
└┴─────────┴┴─────────┴┴─────────┴┴─────────┴┘
┌┬────────────────────┬┬─────────┬┬─────────┬┐
││     Format You     ││  Some   ││ Tables  ││
├┼────────────────────┴┴─────────┴┴─────────┼┤
││                   FYST                   ││
└┴──────────────────────────────────────────┴┘
"""
```