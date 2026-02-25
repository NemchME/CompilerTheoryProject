from __future__ import annotations
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    line: int
    col: int


KEYWORDS = {
    "program", "var", "begin", "end",
    "integer", "char", "boolean",
    "if", "then", "else",
    "while", "do",
    "for", "to", "downto",
    "break", "continue",
    "write", "writeln", "read", "readln",
    "div", "mod", "not", "and", "or",
    "true", "false",
}

MULTI = {":=", "<=", ">=", "<>"}
SINGLE = set("+-*/=<>();:.,")


def tokenize(text: str) -> List[Token]:
    tokens: List[Token] = []
    i = 0
    line, col = 1, 1

    def adv(n: int = 1):
        nonlocal i, line, col
        for _ in range(n):
            if i < len(text) and text[i] == "\n":
                line += 1
                col = 1
            else:
                col += 1
            i += 1

    while i < len(text):
        ch = text[i]

        if ch.isspace():
            adv(1)
            continue

        if ch == "{":
            adv(1)
            while i < len(text) and text[i] != "}":
                adv(1)
            if i < len(text) and text[i] == "}":
                adv(1)
            continue
        if ch == "/" and i + 1 < len(text) and text[i + 1] == "/":
            adv(2)
            while i < len(text) and text[i] != "\n":
                adv(1)
            continue

        two = text[i:i+2]
        if two in MULTI:
            tokens.append(Token("OP", two, line, col))
            adv(2)
            continue

        if ch in SINGLE:
            if ch in "+-*/=<>":
                kind = "OP"
            else:
                kind = "SYM"
            tokens.append(Token(kind, ch, line, col))
            adv(1)
            continue

        if ch.isdigit():
            start_line, start_col = line, col
            s = ""
            while i < len(text) and text[i].isdigit():
                s += text[i]
                adv(1)
            tokens.append(Token("INT", s, start_line, start_col))
            continue

        if ch == "'":
            start_line, start_col = line, col
            adv(1)
            if i >= len(text):
                raise SyntaxError(f"Unterminated char literal at {start_line}:{start_col}")
            c = text[i]
            adv(1)
            if i >= len(text) or text[i] != "'":
                raise SyntaxError(f"Invalid char literal at {start_line}:{start_col}")
            adv(1)
            tokens.append(Token("CHAR", c, start_line, start_col))
            continue

        if ch.isalpha() or ch == "_":
            start_line, start_col = line, col
            s = ""
            while i < len(text) and (text[i].isalnum() or text[i] == "_"):
                s += text[i]
                adv(1)
            low = s.lower()
            if low in KEYWORDS:
                tokens.append(Token("KW", low, start_line, start_col))
            else:
                tokens.append(Token("IDENT", s, start_line, start_col))
            continue

        raise SyntaxError(f"Unexpected char {ch!r} at {line}:{col}")

    tokens.append(Token("EOF", "", line, col))
    return tokens