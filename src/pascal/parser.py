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

    def parse_stmt(self) -> ast.Stmt:
        if self.peek("KW", "if"):
            return self.parse_if()
        if self.peek("KW", "while"):
            return self.parse_while()
        if self.peek("IDENT"):
            name = self.expect("IDENT").value
            self.expect("OP", ":=")
            expr = self.parse_expr()
            return ast.Assign(target=name, expr=expr)
        t = self.curr()
        raise PascalParserError(f"Unknown statement at {t.line}:{t.col}: {t.kind}:{t.value}")

    def parse_if(self) -> ast.If:
        self.expect("KW", "if")
        cond = self.parse_expr()
        self.expect("KW", "then")
        then_branch = self.parse_single_or_block_stmt()
        else_branch = None
        if self.peek("KW", "else"):
            self.advance()
            else_branch = self.parse_single_or_block_stmt()
        return ast.If(cond=cond, then_branch=then_branch, else_branch=else_branch)

    def parse_while(self) -> ast.While:
        self.expect("KW", "while")
        cond = self.parse_expr()
        self.expect("KW", "do")
        body = self.parse_single_or_block_stmt()
        return ast.While(cond=cond, body=body)

    def parse_single_or_block_stmt(self) -> List[ast.Stmt]:
        if self.peek("KW", "begin"):
            self.advance()
            stmts = self.parse_stmt_list(until_kw="end")
            self.expect("KW", "end")
            return stmts
        return [self.parse_stmt()]

    def parse_expr(self) -> ast.Expr:
        return self.parse_rel()

    def parse_rel(self) -> ast.Expr:
        left = self.parse_add()
        if self.peek("OP") and self.curr().value in ("=", "<>", "<", "<=", ">", ">="):
            op = self.advance().value
            right = self.parse_add()
            return ast.BinOp(op=op, left=left, right=right)
        return left

    def parse_add(self) -> ast.Expr:
        left = self.parse_mul()
        while self.peek("OP") and self.curr().value in ("+", "-"):
            op = self.advance().value
            right = self.parse_mul()
            left = ast.BinOp(op=op, left=left, right=right)
        return left

    def parse_mul(self) -> ast.Expr:
        left = self.parse_unary()
        while True:
            if self.peek("OP") and self.curr().value in ("*", "/"):
                op = self.advance().value
            elif self.peek("KW") and self.curr().value in ("div", "mod"):
                op = self.advance().value
            else:
                break
            right = self.parse_unary()
            left = ast.BinOp(op=op, left=left, right=right)
        return left

    def parse_unary(self) -> ast.Expr:
        if self.peek("KW", "not"):
            self.advance()
            return ast.UnOp(op="not", operand=self.parse_unary())
        if self.peek("OP") and self.curr().value in ("+", "-"):
            op = self.advance().value
            return ast.UnOp(op=op, operand=self.parse_unary())
        return self.parse_primary()

    def parse_primary(self) -> ast.Expr:
        if self.peek("INT"):
            v = int(self.advance().value)
            return ast.Literal(value=v)
        if self.peek("CHAR"):
            c = self.advance().value
            return ast.Literal(value=c)
        if self.peek("KW") and self.curr().value in ("true", "false"):
            b = self.advance().value == "true"
            return ast.Literal(value=b)
        if self.peek("IDENT"):
            return ast.Ident(name=self.advance().value)
        if self.peek("SYM", "("):
            self.advance()
            e = self.parse_expr()
            self.expect("SYM", ")")
            return e
        t = self.curr()
        raise PascalParserError(f"Expected expression at {t.line}:{t.col}, got {t.kind}:{t.value}")