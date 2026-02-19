from contextlib import suppress
from typing import Union


class ParsingError(Exception):

    def __init__(self, message: str):
        super().__init__(message)


class BaseParser:

    def __init__(self, text: str):
        self.text = text
        self.pos = 0

    @property
    def curr(self) -> str:
        return self.text[self.pos] if self.pos < len(self.text) else '$'

    def ws(self):
        while self.curr.isspace():
            self.pos += 1

    def parse(self, s1: str, *s: str) -> Union[str, None]:
        self.ws()
        for ss in (s1, *s):
            if self.text[self.pos:self.pos + len(ss)] == ss:
                self.pos += len(ss)
                self.ws()
                return ss
        raise ParsingError(f"Expected one of {s1, *s} at pos={self.pos}")

    def is_parse(self, s1: str, *s: str) -> Union[str, None]:
        pos = self.pos
        res = None
        with suppress(ParsingError):
            res = self.parse(s1, *s)
        self.pos = pos
        return res