import string
from typing import NamedTuple, List, Literal
import sys


class Token(NamedTuple):
    kind: str
    value: str
    line: int


def error(line: int, msg: str):
    print(f"Scanning Error at line {line}: {msg}")
    sys.exit(1)


class Scanner:
    def __init__(
        self, input: str, reserved: List[str] = [], punctuation: List[str] = []
    ):
        self.index: int = 0
        self.reserved = reserved
        self.punctuation = punctuation
        self.tokens: list[Token] = self.scan(input)

    def scan(self, input: str) -> List[Token]:
        retval: List[Token] = []
        index: int = 0
        lineno: int = 1
        t: Token = Token("", "", -1)

        while index < len(input):
            ch = input[index]
            if ch == "\n":
                lineno += 1
                index += 1
            elif ch == "/" and index < len(input) - 1 and input[index + 1] == "/":
                index += 2  # skip both /'s
                while index < len(input) and input[index] != "\n":
                    index += 1
            elif ch in string.whitespace:
                index += 1
            elif ch == '"' or ch == "'":
                delimiter = ch
                value = ""
                index += 1
                while (
                    index < len(input)
                    and input[index] != delimiter
                    and input[index] != "\n"
                ):
                    value += input[index]
                    index += 1
                if index == len(input) or input[index] == "\n":
                    error(lineno, "Unterminated string")
                t = Token("STR", value, lineno)
                retval.append(t)
                index += 1
            elif ch in string.ascii_letters:
                value = ""
                while index < len(input) and input[index] in (
                    string.ascii_letters + string.digits
                ):
                    value += input[index]
                    index += 1
                if value in self.reserved:
                    t = Token(value, value, lineno)
                else:
                    t = Token("ID", value, lineno)
                retval.append(t)
            elif ch in string.digits or ch == "-":
                if ch == "-":
                    index += 1
                    value = "-"
                else:
                    value = ""
                while index < len(input) and input[index] in string.digits:
                    value += input[index]
                    index += 1
                assert value != "-", "Missing integer literal after -"
                t = Token("INT", value, lineno)
                retval.append(t)
            else:
                for exact in self.punctuation:
                    if (
                        index + len(exact) <= len(input)
                        and exact == input[index : index + len(exact)]
                    ):
                        t = Token(exact, exact, lineno)
                        index += len(exact)
                        break
                if t is None:
                    assert False, f"{lineno}: unexpected character, '{ch}'"
                retval.append(t)
        t: Token = Token("EOF", "", lineno)
        retval.append(t)
        return retval

    def peek(self) -> Token:
        return self.tokens[self.index]

    def consume(self) -> Token:
        t = self.peek()
        self.index += 1
        return t
