from __future__ import annotations
from pathlib import Path
from lark import Lark, Transformer, UnexpectedInput

from src.ast import nodes as ast


class PascalParserError(Exception):
    pass

class ASTBuilder(Transformer):
    binary_ops = {
        "bin_or": ast.BinaryOpKind.OR,
        "bin_and": ast.BinaryOpKind.AND,
        "bin_eq": ast.BinaryOpKind.EQ,
        "bin_ne": ast.BinaryOpKind.NE,
        "bin_lt": ast.BinaryOpKind.LT,
        "bin_le": ast.BinaryOpKind.LE,
        "bin_gt": ast.BinaryOpKind.GT,
        "bin_ge": ast.BinaryOpKind.GE,
        "bin_add": ast.BinaryOpKind.ADD,
        "bin_sub": ast.BinaryOpKind.SUB,
        "bin_mul": ast.BinaryOpKind.MUL,
        "bin_float_div": ast.BinaryOpKind.FLOAT_DIV,
        "bin_int_div": ast.BinaryOpKind.INT_DIV,
        "bin_mod": ast.BinaryOpKind.MOD,
    }
    unary_ops = {
        "un_not": ast.UnaryOpKind.NOT,
        "un_plus": ast.UnaryOpKind.PLUS,
        "un_minus": ast.UnaryOpKind.MINUS,
    }

    @staticmethod
    def program(items):
        return ast.Program(name=str(items[0]), block=items[1])

    @staticmethod
    def block(items):
        if len(items) == 1:
            return ast.Block(var_decls=[], body=items[0])
        return ast.Block(var_decls=items[0], body=items[1])

    @staticmethod
    def var_section(items):
        decls = []
        for item in items:
            decls.extend(item)
        return decls

    @staticmethod
    def var_decl(items):
        names = items[0]
        type_name = items[1]
        return [ast.VarDecl(ident=ast.Ident(name=name), type_name=type_name) for name in names]

    @staticmethod
    def ident_list(items):
        return [str(item) for item in items]

    @staticmethod
    def type_name(items):
        return str(items[0])

    @staticmethod
    def compound_stmt(items):
        if not items:
            return ast.CompoundStmt(statements=[])
        return items[0]

    @staticmethod
    def stmt_list(items):
        return ast.CompoundStmt(statements=items)

    def if_stmt(self, items):
        cond = items[0]
        then_branch = self._to_compound(items[1])
        else_branch = self._to_compound(items[2]) if len(items) == 3 else None
        return ast.If(cond=cond, then_branch=then_branch, else_branch=else_branch)

    def while_stmt(self, items):
        return ast.While(cond=items[0], body=self._to_compound(items[1]))

    def for_stmt(self, items):
        return ast.For(
            ident=ast.Ident(name=str(items[0])),
            start=items[1],
            direction=str(items[2]),
            end=items[3],
            body=self._to_compound(items[4]),
        )

    @staticmethod
    def for_dir(items):
        return str(items[0])

    @staticmethod
    def break_stmt(_):
        return ast.Break()

    @staticmethod
    def continue_stmt(_):
        return ast.Continue()

    @staticmethod
    def assign_stmt(items):
        return ast.Assign(ident=ast.Ident(name=str(items[0])), expr=items[1])

    @staticmethod
    def call_stmt(items):
        return items[0]

    @staticmethod
    def call(items):
        func = ast.Ident(name=str(items[0]))
        args = items[1] if len(items) == 2 else []
        return ast.Call(func=func, args=args)

    @staticmethod
    def call_name(items):
        return str(items[0])

    @staticmethod
    def arg_list(items):
        return list(items)

    @staticmethod
    def int_lit(items):
        return ast.Literal(value=int(items[0]))

    @staticmethod
    def char_lit(items):
        value = str(items[0])[1:-1]
        return ast.Literal(value=value)

    @staticmethod
    def true_lit(_):
        return ast.Literal(value=True)

    @staticmethod
    def false_lit(_):
        return ast.Literal(value=False)

    @staticmethod
    def ident(items):
        return ast.Ident(name=str(items[0]))

    def __getattr__(self, name):
        if name in self.binary_ops:
            return lambda items: ast.BinOp(left=items[0], op=self.binary_ops[name], right=items[1])
        if name in self.unary_ops:
            return lambda items: ast.UnOp(op=self.unary_ops[name], expr=items[0])
        raise AttributeError(name)

    @staticmethod
    def _to_compound(stmt):
        if isinstance(stmt, ast.CompoundStmt):
            return stmt
        return ast.CompoundStmt(statements=[stmt])

class PascalParser:

    def __init__(self, text: str):
        self.text = text
        grammar_path = Path(__file__).with_name("pascal.lark")
        grammar = grammar_path.read_text(encoding="utf-8")
        self.parser = Lark(grammar, start="program", parser="lalr")

    def parse_program(self) -> ast.Program:
        try:
            tree = self.parser.parse(self.text)
            return ASTBuilder().transform(tree)
        except UnexpectedInput as error:
            raise PascalParserError(str(error)) from error
