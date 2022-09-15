"""
Course: CSC 453 - Compilers; Fall 2022
Author: Hung Tran (hungtr@arizona.edu)
Due date: 2022/09/15
Assg: Milestone 2 - Scanner
Goals: Write a scanner for Omega 
"""
# Students will edit this file

from error import error
from tokens import keywords, punctuation, Coord, Token

class Scanner:
    def __init__(self, input: str):
        """Create a new scanner for the given input string."""

    def peek(self) -> Token:
        """Return the next token without consuming it."""

    def consume(self) -> Token:
        """Advance the scanner and return the token that was
        current before advancing."""

    def match(self, kind: str) -> Token:
        if self.peek().kind == kind:
            return self.consume()
        else:
            error.error(f"expected {kind}, got {self.peek().kind}", self.peek().coord)
