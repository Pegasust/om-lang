"""
Course: CSC 453 - Compilers; Fall 2022
Author: Hung Tran (hungtr@arizona.edu)
Due date: 2022/09/15
Assg: Milestone 2 - Scanner
Goals: Write a scanner for Omega 
"""
# Students will edit this file

from functools import wraps
from typing import Callable, Dict, Generic, TypeVar, Union

import string
from error import error
from tokens import keywords, punctuation, Coord, Token

T = TypeVar('T')
E = TypeVar('E')
T1 = TypeVar('T1')
E1 = TypeVar('E1')

class Result(Generic[T, E]):
    def __init__(self, value: Union[T, E], has_err: bool):
        self.value = value
        self.has_err = has_err
    def is_ok(self) -> bool:
        return not self.has_err
    def is_err(self) -> bool:
        return self.has_err
    @classmethod
    def ok(cls, value: T):
        return cls(value, False)
    @classmethod
    def err(cls, value: E):
        return cls(value, True)

class InvalidCharacterErr(Result[T, str]):
    def __init__(self, char: str, coord: Coord, line: Union[None,str]=None):
        line = '' if line is None else f"{line}\n"
        super().__init__(f"{line}Invalid character '{char}'@{coord}", True)

class Scanner:
    def __init__(self, input: str):
        """Create a new scanner for the given input string."""
        # constexpr values from specs
        self.punc_map: Dict[str, list[str]] = dict()
        print(f"Input: \"\"\"{input}\"\"\";")
        for punc in punctuation:
            self.punc_map.setdefault(punc[0], []).append(punc)

        self.tokens = self._parse_tokens(input)
        # tok_str = "\n".join([f"Token('{tok.kind}','{tok.value} @ {tok.coord}')" for tok in self.tokens])
        # print(f"Tokens:\n{tok_str}")
        self.current_idx = 0

    def _parse_line(self, line: str, line_idx: int)->list[Token]:
        retval: list[Token] = []
        # TODO: turn this into a functional programming madness :)
        tok_start_idx = 0
        while tok_start_idx < len(line):
            def const_kind(kind: str) -> Callable[[str],str]:
                return lambda _: kind
            def span_token(kind: Callable[[str],str], span_result: Callable[[int, str], 
                    Result[bool, str]]) -> Result[Token, str]:
                nonlocal tok_start_idx
                end_idx = tok_start_idx
                while end_idx < len(line):
                    res = span_result(end_idx, line[end_idx])
                    if res.is_err():
                        assert(isinstance(res.value, str))
                        return Result.err(res.value)
                    if res.is_ok() and not res.value:
                        break
                    end_idx += 1
                coord = Coord(tok_start_idx + 1, line_idx + 1)
                token_value = line[tok_start_idx:end_idx]
                retval = Token(kind(token_value), token_value, coord)
                tok_start_idx = end_idx - 1
                return Result.ok(retval)

            start_char = line[tok_start_idx]
            token_res: Result[Token, str]
            coord = Coord(tok_start_idx + 1, line_idx + 1)
            if start_char == ' ':
                tok_start_idx += 1
                continue
            elif start_char in string.digits:
                token_res = span_token(const_kind("INT"), 
                    lambda idx, s: Result.ok(s in string.digits + '_') \
                        if not s.isalpha() \
                        else InvalidCharacterErr(s, Coord(idx+1, line_idx+1), line))
            elif start_char in string.ascii_letters + '_':
                kind: Callable[[str], str] = \
                    lambda s: s if s in keywords else "ID"
                token_res = span_token(kind, lambda idx, s: Result.ok(s.isalnum() or s in '_'))
            elif start_char in self.punc_map:
                match = {v for v in self.punc_map[start_char] if len(v) == 1}
                possible = {v for v in self.punc_map[start_char]} - match
                end_idx = tok_start_idx + 1
                while end_idx < len(line):
                    s = line[end_idx]
                    tok_offset = end_idx - tok_start_idx
                    next_match = {v for v in possible if v[tok_offset] == s}
                    if len(next_match) == 0:
                        break
                    match = next_match
                    possible = possible - next_match
                    end_idx += 1

                match_str = match.pop()
                token_res = Result.ok(Token(match_str, match_str, coord))
                tok_start_idx = end_idx - 1
            else:
                token_res = InvalidCharacterErr(start_char, coord, line)
            if token_res.is_err():
                assert(isinstance(token_res.value, str))
                raise ValueError(token_res.value)
            tok_start_idx += 1
            assert(isinstance(token_res.value, Token))
            retval.append(token_res.value)
        return retval

    def _parse_tokens(self, input: str) -> list[Token]:
        retval = []
        lines = input.splitlines()
        for line_idx, line in enumerate(lines):
            tokens = self._parse_line(line, line_idx)
            retval.extend(tokens)
        
        tok = Token("EOF","EOF",
            Coord(1+(len(lines[-1]) if len(lines) > 0 else 1), len(lines)))
        retval.append(tok)
        return retval

    def peek(self) -> Token:
        """Return the next token without consuming it."""
        return self.tokens[self.current_idx]

    def consume(self) -> Token:
        """Advance the scanner and return the token that was
        current before advancing."""
        v = self.peek()
        # short-circuit behavior
        self.current_idx = min(self.current_idx + 1, len(self.tokens)-1)
        return v
        

    def match(self, kind: str) -> Token:
        if self.peek().kind == kind:
            return self.consume()
        else:
            error(f"expected {kind}, got {self.peek().kind}", self.peek().coord)


def main():
    def dump_tokens(scanner: Scanner):
        tokens: list[Token] = []
        while True:
            tok = scanner.consume()
            tokens.append(tok)
            if tok.kind == "EOF":
                break
        return "\n".join([
            f"Token({tok.kind},{tok.value})@{tok.coord.line}:{tok.coord.col}" 
            for tok in tokens
        ])
    print("Enter tests here")
    line = ""
    while not line.startswith("QUIT"):
        line = input("> ")
        scanner = Scanner(line)
        print(f"Tokens:\n{dump_tokens(scanner)}")
if __name__ == "__main__":
    main()

