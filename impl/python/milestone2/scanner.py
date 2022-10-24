"""
Course: CSC 453 - Compilers; Fall 2022
Author: Hung Tran (hungtr@arizona.edu)
Due date: 2022/09/15
Assg: Milestone 2 - Scanner
Goals: Write a scanner for Omega 
"""
# Students will edit this file

from typing import Iterable, Optional, Tuple, TypeVar
from error import error
from tokens import keywords, punctuation, Coord, Token

class Scanner:
    def __init__(self, input: str):
        """Create a new scanner for the given input string."""
        self.keywords = set(keywords)
        self.punctuations = set(punctuation)
        self._tokens = (self._parse_token(coord, word) for coord, word in self._words(input))
        self.tokens = list(self._tokens)
        self.has_err = any((tok is None for tok in self.tokens))
        self.memento = self.tokens[0] if len(self.tokens) > 0 else None
    
    def _tokens(self, input: str) -> Iterable[Optional[Token]]:

    def _words(self, input: str) -> Iterable[Tuple[Coord, str]]:
        """
        Returns a generator that creates proper coordinate and the word
        """
        for line_idx, line in enumerate(input):
            word_start = 0
            word = ""
            for col, c in enumerate(line):
                if not c.isspace():
                    word += c
                    continue
                if len(word) == 0:
                    continue
                yield (Coord(word_start + 1, line_idx + 1), word)
                word = ""
                word_start = col + 1
            if len(word) != 0:
                yield (Coord(word_start + 1, line_idx + 1), word)

    def _kind(self, word: str) -> Optional[str]:
        """
        Determines the kind of a given word
        """
        if word in keywords or word in punctuation:
            return word
        if word[0].isalpha() and word[1:].isalnum():
            return "ID"
        if word.isnumeric():
            return "INT"
        return None 

    def _parse_token(self, coord: Coord, word: str) -> Optional[Token]:
        kind = self._kind(word)
        return Token(kind, word, coord) if kind is not None else None

    def peek(self) -> Optional[Token]:
        """Return the next token without consuming it."""
        return self.memento

    def consume(self) -> Optional[Token]:
        """Advance the scanner and return the token that was
        current before advancing."""

    def match(self, kind: str) -> Token:
        if self.peek().kind == kind:
            return self.consume()
        else:
            error(f"expected {kind}, got {self.peek().kind}", self.peek().coord)

    
