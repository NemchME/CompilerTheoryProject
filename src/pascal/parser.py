from __future__ import annotations
from pathlib import Path
from lark import Lark, Transformer, UnexpectedInput, Token

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
    def _line_from(item):
        if isinstance(item, Token):
            return item.line, item.column
        return getattr(item, 'row', None), getattr(item, 'col', None)

    def _set_pos_from(self, node, item):
        row, col = self._line_from(item)
        node.row = row
        node.col = col
        return node

    def program(self, items):
        node = ast.Program(name=str(items[0]), block=items[1])
        return self._set_pos_from(node, items[0])

    def block(self, items):
        var_decls = []
        func_decls = []
        body = ast.CompoundStmt([])
        for item in items:
            if isinstance(item, list) and item:
                if isinstance(item[0], ast.VarDecl):
                    var_decls = item
                elif isinstance(item[0], ast.Func):
                    func_decls = item
            elif isinstance(item, ast.Func):
                func_decls.append(item)
            else:
                body = item
        node = ast.Block(var_decls=var_decls, func_decls=func_decls, body=body)
        return self._set_pos_from(node, body if body else (var_decls[0] if var_decls else None))

    def var_section(self, items):
        decls = []
        for item in items:
            decls.extend(item)
        return decls

    def var_decl(self, items):
        names = items[0]
        type_name = str(items[1])
        result = []
        for name in names:
            ident = ast.Ident(name=name)
            ident.row = getattr(name, 'line', None)
            ident.col = getattr(name, 'column', None)
            node = ast.VarDecl(ident=ident, type_name=type_name)
            node.row = ident.row
            node.col = ident.col
            result.append(node)
        return result

    def ident_list(self, items):
        return list(items)

    def func_decl(self, items):
        name_token = items[0]
        name = ast.Ident(name=str(name_token))
        name.row = getattr(name_token, 'line', None)
        name.col = getattr(name_token, 'column', None)
        if len(items) == 4:
            params, return_type, block = items[1], str(items[2]), items[3]
        else:
            params, return_type, block = [], str(items[1]), items[2]
        node = ast.Func(name=name, params=params, return_type=return_type, block=block)
        return self._set_pos_from(node, name_token)

    def params(self, items):
        params = []
        for item in items:
            if isinstance(item, list):
                params.extend(item)
            else:
                params.append(item)
        return params

    def param(self, items):
        names = items[0]
        type_name = str(items[1])
        result = []
        for name in names:
            ident = ast.Ident(name=str(name))
            ident.row = getattr(name, 'line', None)
            ident.col = getattr(name, 'column', None)
            node = ast.VarDecl(ident=ident, type_name=type_name)
            node.row = ident.row
            node.col = ident.col
            result.append(node)
        return result

    def compound_stmt(self, items):
        if items:
            return items[0]
        node = ast.CompoundStmt(statements=[])
        node.row = node.col = None
        return node

    def stmt_list(self, items):
        node = ast.CompoundStmt(statements=items)
        return self._set_pos_from(node, items[0] if items else None)

    def if_stmt(self, items):
        cond = items[0]
        node = ast.If(cond=cond, then_branch=self._to_compound(items[1]), else_branch=self._to_compound(items[2]) if len(items) == 3 else None)
        return self._set_pos_from(node, cond)

    def while_stmt(self, items):
        node = ast.While(cond=items[0], body=self._to_compound(items[1]))
        return self._set_pos_from(node, items[0])

    def for_stmt(self, items):
        ident_token = items[0]
        ident = ast.Ident(name=str(ident_token))
        ident.row = getattr(ident_token, 'line', None)
        ident.col = getattr(ident_token, 'column', None)
        node = ast.For(ident=ident, start=items[1], direction=str(items[2]), end=items[3], body=self._to_compound(items[4]))
        return self._set_pos_from(node, ident)

    def break_stmt(self, _):
        return ast.Break()

    def continue_stmt(self, _):
        return ast.Continue()

    def return_stmt(self, items):
        node = ast.Return(expr=items[0] if items else None)
        return self._set_pos_from(node, items[0] if items else None)

    def assign_stmt(self, items):
        ident_token = items[0]
        ident = ast.Ident(name=str(ident_token))
        ident.row = getattr(ident_token, 'line', None)
        ident.col = getattr(ident_token, 'column', None)
        node = ast.Assign(ident=ident, expr=items[1])
        return self._set_pos_from(node, ident)

    def call_stmt(self, items):
        return items[0]

    def call(self, items):
        token = items[0]
        func = ast.Ident(name=str(token))
        func.row = getattr(token, 'line', None)
        func.col = getattr(token, 'column', None)
        node = ast.Call(func=func, args=items[1] if len(items) == 2 else [])
        return self._set_pos_from(node, func)

    def call_name(self, items):
        return items[0]

    def arg_list(self, items):
        return list(items)

    def int_lit(self, items):
        token = items[0]
        node = ast.Literal(value=int(token))
        return self._set_pos_from(node, token)

    def char_lit(self, items):
        token = items[0]
        node = ast.Literal(value=str(token)[1:-1])
        return self._set_pos_from(node, token)

    def true_lit(self, _):
        return ast.Literal(value=True)

    def false_lit(self, _):
        return ast.Literal(value=False)

    def ident(self, items):
        token = items[0]
        node = ast.Ident(name=str(token))
        return self._set_pos_from(node, token)

    def _make_bin(self, items, op):
        node = ast.BinOp(left=items[0], op=op, right=items[1])
        return self._set_pos_from(node, items[0])

    def _make_un(self, items, op):
        node = ast.UnOp(op=op, expr=items[0])
        return self._set_pos_from(node, items[0])

    def int_lit(self, items):
        token = items[0]
        node = ast.Literal(value=int(token))
        return self._set_pos_from(node, token)

    def real_lit(self, items):
        token = items[0]
        node = ast.Literal(value=float(token))
        return self._set_pos_from(node, token)

    def char_lit(self, items):
        token = items[0]
        node = ast.Literal(value=str(token)[1:-1])
        return self._set_pos_from(node, token)

    def true_lit(self, _):
        return ast.Literal(value=True)

    def false_lit(self, _):
        return ast.Literal(value=False)

    def cast(self, items):
        token = items[0]
        type_name = token.value if hasattr(token, "value") else str(token)
        expr = items[1]
        node = ast.Cast(type_name, expr)
        return self._set_pos_from(node, token)


    def __getattr__(self, name):
        if name in self.binary_ops:
            return lambda items: self._make_bin(items, self.binary_ops[name])
        if name in self.unary_ops:
            return lambda items: self._make_un(items, self.unary_ops[name])
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
        self.parser = Lark(grammar, start="program", parser="lalr", propagate_positions=True)

    def parse_program(self) -> ast.Program:
        try:
            tree = self.parser.parse(self.text)
            return ASTBuilder().transform(tree)
        except UnexpectedInput as error:
            raise PascalParserError(str(error)) from error
