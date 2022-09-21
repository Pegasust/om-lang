"""
Course: CSC 453 - Compilers; Fall 2022
Author: Hung Tran (hungtr@arizona.edu)
Due date: 2022/09/15
Assg: Milestone 2 - Scanner
Goals: Write a scanner for Omega 
"""
# Students will edit this file

from functools import reduce
from typing import Callable, Dict, Iterable, Optional, Tuple, TypeVar
from error import error
from tokens import keywords, punctuation, Coord, Token

class Scanner:
    def __init__(self, input: str):
        """Create a new scanner for the given input string."""
        # constexpr values from specs
        self.punc_map: Dict[str, list[str]] = dict()
        for punc in punctuation:
            self.punc_map.setdefault(punc[0], []).append(punc)

        self.tokens = self._parse_tokens(input)
        self.current_idx = 0

    def _parse_tokens(self, input: str) -> list[Token]:
        retval = []
        for line_idx, line in enumerate(input.splitlines()):
            # TODO: turn this into a functional programming madness :)
            tok_start_idx = 0
            while tok_start_idx < len(line):
                def span_token(kind: str, span_criteria: Callable[[int, str], bool]) -> Token:
                    nonlocal tok_start_idx
                    tok_end_idx = tok_start_idx
                    while tok_end_idx < len(line):
                        tok_end_idx += 1
                        if span_criteria(tok_end_idx, line[tok_end_idx]):
                            break
                    coord = Coord(tok_start_idx + 1, line_idx + 1)
                    token_value = line[tok_start_idx:tok_end_idx]
                    retval = Token(kind, token_value, coord)
                    tok_start_idx = tok_end_idx - 1
                    return retval

                start_char = line[tok_start_idx]
                if start_char.isnumeric():
                    # search for the end of int or EOL
                    retval.append(span_token("INT", lambda _, s: s.isnumeric()))
                elif start_char.isalpha():
                    retval.append(span_token("ID", lambda _, s: s.isalnum()))
                elif start_char in self.punc_map:
                    # The language plays nicely here, no repeating single char
                    # so we can just pass ahead in linear time
                    match = {v for v in self.punc_map[start_char] if len(v) == 1}
                    possible = {v for v in self.punc_map[start_char]} - match
                    tok_offset = 0
                    while tok_offset < len(line)-tok_start_idx:
                        tok_offset += 1
                        s = line[tok_start_idx + tok_offset]
                        next_match = {v for v in possible if v[tok_offset] == s}
                        if len(next_match) == 0:
                            break
                    match_str = match.pop()
                    coord = Coord(tok_start_idx + 1, line_idx + 1)
                    retval.append(Token(match_str, match_str, coord))
                    tok_start_idx += tok_offset-1
                    
                tok_start_idx += 1
        return retval
            


    def peek(self) -> Token:
        """Return the next token without consuming it."""
        return self.tokens[self.current_idx]

    def consume(self) -> Token:
        """Advance the scanner and return the token that was
        current before advancing."""
        v = self.peek()
        # short-circuit behavior
        self.current_idx = min(self.current_idx, len(self.tokens)-1)
        return v
        

    def match(self, kind: str) -> Token:
        if self.peek().kind == kind:
            return self.consume()
        else:
            error(f"expected {kind}, got {self.peek().kind}", self.peek().coord)

def main():
    scanner = Scanner("")

if __name__ == "__main__":
    main()

