from __future__ import annotations
from typing import List, Optional

from src.pascal.lexer import Token, tokenize
from src.ast import nodes as ast


class PascalParserError(Exception):
    pass


class PascalParser:
    def __init__(self, text: str):
        self.tokens: List[Token] = tokenize(text)
        self.i = 0

    def curr(self) -> Token:
        return self.tokens[self.i]

    def peek(self, kind: str, value: Optional[str] = None) -> bool:
        t = self.curr()
        if t.kind != kind:
            return False
        if value is not None and t.value != value:
            return False
        return True

    def advance(self) -> Token:
        t = self.curr()
        if t.kind != "EOF":
            self.i += 1
        return t

    def expect(self, kind: str, value: Optional[str] = None) -> Token:
        t = self.curr()
        if not self.peek(kind, value):
            expected = f"{kind}:{value}" if value else kind
            raise PascalParserError(
                f"Expected {expected}, got {t.kind}:{t.value} at {t.line}:{t.col}"
            )
        return self.advance()

    # далее будут правила грамматики

    def parse_program(self) -> ast.Program:
        raise NotImplementedError