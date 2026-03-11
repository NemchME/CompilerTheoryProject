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
        stmts = self.parse_stmt_list("end")
        self.expect("KW", "end")
        return ast.Block(var_decls=var_decls, body=ast.CompoundStmt(stmts))

    def parse_var_section(self) -> List[ast.VarDecl]:
        decls: List[ast.VarDecl] = []
        self.expect("KW", "var")

        while self.peek("IDENT"):
            names = [self.expect("IDENT").value]

            while self.peek("SYM", ","):
                self.advance()
                names.append(self.expect("IDENT").value)

            self.expect("SYM", ":")
            type_tok = self.expect("KW")
            self.expect("SYM", ";")

            for name in names:
                decls.append(
                    ast.VarDecl(
                        ident=ast.Ident(name=name),
                        type_name=type_tok.value
                    )
                )

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
                        f"Expected ';' or '{until_kw}', got {t.kind}:{t.value}"
                    )

        return stmts

    def parse_stmt(self) -> ast.Stmt:
        if self.peek("KW", "if"):
            return self.parse_if()

        if self.peek("KW", "while"):
            return self.parse_while()

        if self.peek("KW", "for"):
            return self.parse_for()

        if self.peek("KW", "break"):
            self.advance()
            return ast.Break()

        if self.peek("KW", "continue"):
            self.advance()
            return ast.Continue()

        if self.peek("KW") and self.curr().value in ("write", "writeln"):
            return self.parse_write()

        if self.peek("KW") and self.curr().value in ("read", "readln"):
            return self.parse_read()

        if self.peek("IDENT"):
            name = self.expect("IDENT").value
            self.expect("OP", ":=")
            expr = self.parse_expr()

            return ast.Assign(
                target=ast.Ident(name=name),
                value=expr
            )

        t = self.curr()
        raise PascalParserError(f"Unknown statement {t.kind}:{t.value}")

    def parse_if(self) -> ast.If:
        self.expect("KW", "if")
        cond = self.parse_expr()
        self.expect("KW", "then")

        then_branch = ast.CompoundStmt(self.parse_single_or_block())

        else_branch = None
        if self.peek("KW", "else"):
            self.advance()
            else_branch = ast.CompoundStmt(self.parse_single_or_block())

        return ast.If(cond, then_branch, else_branch)

    def parse_while(self) -> ast.While:
        self.expect("KW", "while")
        cond = self.parse_expr()
        self.expect("KW", "do")

        body = ast.CompoundStmt(self.parse_single_or_block())

        return ast.While(cond, body)

    def parse_for(self) -> ast.For:
        self.expect("KW", "for")

        name = self.expect("IDENT").value

        self.expect("OP", ":=")

        start = self.parse_expr()

        if self.peek("KW", "to"):
            direction = "to"
            self.advance()
        else:
            direction = "downto"
            self.advance()

        end = self.parse_expr()

        self.expect("KW", "do")

        body = ast.CompoundStmt(self.parse_single_or_block())

        return ast.For(
            var=ast.Ident(name=name),
            start=start,
            direction=direction,
            end=end,
            body=body
        )

    def parse_write(self) -> ast.Write:
        kw = self.expect("KW")

        newline = kw.value == "writeln"

        self.expect("SYM", "(")

        expr = None
        if not self.peek("SYM", ")"):
            expr = self.parse_expr()

        self.expect("SYM", ")")

        return ast.Write(expr, newline)

    def parse_read(self) -> ast.Read:
        self.expect("KW")

        self.expect("SYM", "(")

        name = self.expect("IDENT").value

        self.expect("SYM", ")")

        return ast.Read(ast.Ident(name))

    def parse_single_or_block(self) -> List[ast.Stmt]:
        if self.peek("KW", "begin"):
            self.advance()
            stmts = self.parse_stmt_list("end")
            self.expect("KW", "end")
            return stmts

        return [self.parse_stmt()]

    def parse_expr(self) -> ast.Expr:
        left = self.parse_add()

        while self.peek("OP") and self.curr().value in (
            "=", "<>", "<", "<=", ">", ">="
        ):
            op = self.advance().value
            right = self.parse_add()

            mapping = {
                "=": ast.BinaryOpKind.EQ,
                "<>": ast.BinaryOpKind.NE,
                "<": ast.BinaryOpKind.LT,
                "<=": ast.BinaryOpKind.LE,
                ">": ast.BinaryOpKind.GT,
                ">=": ast.BinaryOpKind.GE
            }

            left = ast.BinOp(mapping[op], left, right)

        return left

    def parse_add(self) -> ast.Expr:
        left = self.parse_mul()

        while self.peek("OP") and self.curr().value in ("+", "-"):
            op = self.advance().value
            right = self.parse_mul()

            kind = ast.BinaryOpKind.ADD if op == "+" else ast.BinaryOpKind.SUB

            left = ast.BinOp(kind, left, right)

        return left

    def parse_mul(self) -> ast.Expr:
        left = self.parse_unary()

        while self.peek("OP") and self.curr().value in ("*", "/"):
            op = self.advance().value
            right = self.parse_unary()

            kind = ast.BinaryOpKind.MUL if op == "*" else ast.BinaryOpKind.DIV

            left = ast.BinOp(kind, left, right)

        return left

    def parse_unary(self) -> ast.Expr:
        if self.peek("OP") and self.curr().value == "-":
            self.advance()
            return ast.UnOp(ast.UnaryOpKind.MINUS, self.parse_unary())

        return self.parse_primary()

    def parse_primary(self) -> ast.Expr:
        if self.peek("INT"):
            return ast.Literal(int(self.advance().value))

        if self.peek("IDENT"):
            return ast.Ident(self.advance().value)

        if self.peek("SYM", "("):
            self.advance()
            e = self.parse_expr()
            self.expect("SYM", ")")
            return e

        t = self.curr()
        raise PascalParserError(f"Expected expression {t.kind}:{t.value}")