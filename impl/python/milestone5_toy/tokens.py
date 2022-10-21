import typing


class Coord(typing.NamedTuple):
    col: int
    line: int

    def __str__(self):
        return f"{self.line}:{self.col}"

    def __repr__(self):
        return f"Coord({self.col}, {self.line})"


class Token(typing.NamedTuple):
    kind: str
    value: str
    coord: Coord

    def __repr__(self) -> str:
        return f"Token({self.kind.__repr__()}, {self.value.__repr__()}, {self.coord.__repr__()})"


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

kinds: list[str] = ["id", "int_lit", "string_lit"] + punctuation + keywords
