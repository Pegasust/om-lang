#!/usr/bin/env python3
from dataclasses import dataclass, field
from enum import Enum
from typing import List, TextIO, Tuple, Union, cast

@dataclass
class Cursor:
    line: int
    column: int

class Type(Enum):
    ID='ID'
    INT='INT'

@dataclass
class Token:
    kind: Type
    lexeme: str

class ErrorCode(Enum):
    UNEXPECTED_CHARACTER = 1
    DONE = 0

@dataclass
class Error:
    code: ErrorCode
    explanation: str


@dataclass
class TokenResult:
    """A type inspired by Rust's Result<T,E>"""
    data: Union[Token, Error]
    is_ok: bool

    @classmethod
    def ok(cls, token: Token):
        return cls(token, True)

    @classmethod
    def err(cls, code: ErrorCode, explain: Union[str,None] = None):
        return cls(Error(code, explain or f"${code}"), False)
    

@dataclass
class Scanner:
    sourcefile: TextIO
    _curr: Cursor = \
        field(init=False, repr=True, default=Cursor(0,0))
    _token_idx: int = field(init=False, default=0)
    _memento: Union[TokenResult, None] = field(init=False,default=None)
    _tokens: List[Tuple[str,int]] = field(init=False, default=[])
    
    def next(self) -> TokenResult:
        next_tok = TokenResult.err(ErrorCode.DONE)
        return next_tok
        
    def last(self) -> Union[TokenResult, None]:
        return self._memento

    def current_location(self) -> Cursor:
        # Should ideally copy
        return self._curr

def loop(filepath: str)->Error:
    with open(filepath, "r") as source_f:
        scanner = Scanner(source_f)
        while True:
            tok = scanner.next()
            if not tok.is_ok:
                return cast(Error, tok.data)
            # tok is ok
            curr = scanner.current_location()
            token = cast(Token, tok.data)
            print(f"{curr.line}:{curr.column}:{token.kind.value}:{token.lexeme}")

            
                
def main(filepath: str)->Union[Error,None]:
    err = loop(filepath)
    if err.code == ErrorCode.DONE:
        return None
    return err
        

if __name__ == "__main__":
    import sys
    # hack: only accept 1 param, so an if is sufficient
    if len(sys.argv) < 2:
        print("ERROR: must supply 1 param: filepath", file=sys.stderr)
        exit(1)
    main(sys.argv[1])
