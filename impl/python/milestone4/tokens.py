import typing


class Coord(typing.NamedTuple):
    col: int
    line: int

    def __str__(self):
        return f"{self.line}:{self.col}"


class Token(typing.NamedTuple):
    kind: str
    value: str
    coord: Coord


punctuation: list[str] = [
    ":",
    ",",
    "!=",
    "&",
    "*",
    "/",
    "%",
    "<=",
    "<",
    ">=",
    ">",
    "==",
    "|",
    "=",
    "+",
    "-",
    "[",
    "]",
    "{",
    "}",
    "(",
    ")",
]

keywords: list[str] = [
    "and",
    "bool",
    "call",
    "else",
    "false",
    "func",
    "if",
    "int",
    "length",
    "not",
    "or",
    "print",
    "return",
    "true",
    "var",
    "while",
]

kinds: list[str] = ["id", "int_lit"] + punctuation + keywords
