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

    def parse_program(self) -> ast.Program:
        # program <ident> ; <block> .
        self.expect("KW", "program")
        name = self.expect("IDENT").value
        self.expect("SYM", ";")
        block = self.parse_block()
        self.expect("SYM", ".")
        self.expect("EOF")
        return ast.Program(name=name, block=block)

    def parse_block(self) -> ast.Block:
        var_decls: List[ast.VarDecl] = []
        if self.peek("KW", "var"):
            var_decls = self.parse_var_section()
        self.expect("KW", "begin")
        stmts = self.parse_stmt_list(until_kw="end")
        self.expect("KW", "end")
        return ast.Block(var_decls=var_decls, statements=stmts)

    def parse_var_section(self) -> List[ast.VarDecl]:
        # var ( ident (, ident)* : type ; )+
        decls: List[ast.VarDecl] = []
        self.expect("KW", "var")
        while self.peek("IDENT"):
            names = [self.expect("IDENT").value]
            while self.peek("SYM", ","):
                self.advance()
                names.append(self.expect("IDENT").value)
            self.expect("SYM", ":")
            type_tok = self.expect("KW")  # integer/char/boolean
            if type_tok.value not in ("integer", "char", "boolean"):
                raise PascalParserError(
                    f"Unknown type {type_tok.value} at {type_tok.line}:{type_tok.col}"
                )
            self.expect("SYM", ";")
            decls.append(ast.VarDecl(names=names, type_name=type_tok.value))
        return decls

    def parse_stmt_list(self, until_kw: str) -> List[ast.Stmt]:
        stmts: List[ast.Stmt] = []
        while not self.peek("KW", until_kw):
            stmts.append(self.parse_stmt())
            if self.peek("SYM", ";"):
                self.advance()
                while self.peek("SYM", ";"):
                    self.advance()
            else:
                if not self.peek("KW", until_kw):
                    t = self.curr()
                    raise PascalParserError(
                        f"Expected ';' or '{until_kw}', got {t.kind}:{t.value} at {t.line}:{t.col}"
                    )
        return stmts

    def parse_program(self) -> ast.Program:
        raise NotImplementedError