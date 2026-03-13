from src.ast import nodes as ast
from src.semantics.errors import (
    DuplicateVariableError,
    TypeMismatchError,
    UndefinedVariableError,
)
from src.semantics.symbol_table import SymbolTable, VarSymbol


class SemanticAnalyzer:
    def __init__(self):
        self.symbols = SymbolTable()

    def analyze(self, node: ast.ASTNode) -> None:
        self.visit(node)

    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        raise NotImplementedError(f"No visit method for {type(node).__name__}")

    def visit_Program(self, node: ast.Program):
        self.visit(node.block)

    def visit_Block(self, node: ast.Block):
        for decl in node.var_decls:
            self.visit(decl)
        self.visit(node.body)

    def visit_CompoundStmt(self, node: ast.CompoundStmt):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_VarDecl(self, node: ast.VarDecl):
        type_symbol = self.symbols.lookup(node.type_name)
        if type_symbol is None:
            raise UndefinedVariableError(node.type_name)

        name = node.ident.name
        if self.symbols.has_in_current_scope(name):
            raise DuplicateVariableError(name)

        self.symbols.define(VarSymbol(name=name, type_name=node.type_name))

    def visit_Assign(self, node: ast.Assign):
        name = node.ident.name
        symbol = self.symbols.lookup(name)
        if symbol is None or not isinstance(symbol, VarSymbol):
            raise UndefinedVariableError(name)

        expr_type = self.visit(node.expr)
        if symbol.type_name != expr_type:
            raise TypeMismatchError(symbol.type_name, expr_type)

    def visit_If(self, node: ast.If):
        cond_type = self.visit(node.cond)
        if cond_type != "boolean":
            raise TypeMismatchError("boolean", cond_type)

        self.visit(node.then_branch)

        if node.else_branch is not None:
            self.visit(node.else_branch)

    def visit_While(self, node: ast.While):
        cond_type = self.visit(node.cond)
        if cond_type != "boolean":
            raise TypeMismatchError("boolean", cond_type)

        self.visit(node.body)

    def visit_For(self, node: ast.For):
        name = node.ident.name
        symbol = self.symbols.lookup(name)
        if symbol is None or not isinstance(symbol, VarSymbol):
            raise UndefinedVariableError(name)

        if symbol.type_name != "integer":
            raise TypeMismatchError("integer", symbol.type_name)

        start_type = self.visit(node.start)
        end_type = self.visit(node.end)

        if start_type != "integer":
            raise TypeMismatchError("integer", start_type)
        if end_type != "integer":
            raise TypeMismatchError("integer", end_type)

        self.visit(node.body)

    def visit_Call(self, node: ast.Call):
        func_name = node.func.name.lower()

        if func_name in {"write", "writeln"}:
            for arg in node.args:
                self.visit(arg)
            return None

        if func_name in {"read", "readln"}:
            for arg in node.args:
                if not isinstance(arg, ast.Ident):
                    raise TypeMismatchError("identifier", type(arg).__name__)
                self.visit(arg)
            return "integer"

        for arg in node.args:
            self.visit(arg)

        node.inferred_type = "integer"
        return "integer"

    def visit_Break(self, node: ast.Break):
        return None

    def visit_Continue(self, node: ast.Continue):
        return None

    def visit_Ident(self, node: ast.Ident):
        symbol = self.symbols.lookup(node.name)
        if symbol is None or not isinstance(symbol, VarSymbol):
            raise UndefinedVariableError(node.name)
        node.inferred_type = symbol.type_name
        return symbol.type_name

    def visit_Literal(self, node: ast.Literal):
        if isinstance(node.value, bool):
            node.inferred_type = "boolean"
            return "boolean"
        if isinstance(node.value, int):
            node.inferred_type = "integer"
            return "integer"
        if isinstance(node.value, str) and len(node.value) == 1:
            node.inferred_type = "char"
            return "char"
        raise TypeError(f"Unsupported literal type: {node.value!r}")

    def visit_UnOp(self, node: ast.UnOp):
        expr_type = self.visit(node.expr)

        if node.op == ast.UnaryOpKind.NOT:
            if expr_type != "boolean":
                raise TypeMismatchError("boolean", expr_type)
            node.inferred_type = "boolean"
            return "boolean"

        if node.op in {ast.UnaryOpKind.PLUS, ast.UnaryOpKind.MINUS}:
            if expr_type != "integer":
                raise TypeMismatchError("integer", expr_type)
            node.inferred_type = "integer"
            return "integer"

        raise TypeError(f"Unknown unary operator: {node.op}")

    def visit_BinOp(self, node: ast.BinOp):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        arithmetic_ops = {
            ast.BinaryOpKind.ADD,
            ast.BinaryOpKind.SUB,
            ast.BinaryOpKind.MUL,
            ast.BinaryOpKind.INT_DIV,
            ast.BinaryOpKind.MOD,
        }

        comparison_ops = {
            ast.BinaryOpKind.EQ,
            ast.BinaryOpKind.NE,
            ast.BinaryOpKind.LT,
            ast.BinaryOpKind.LE,
            ast.BinaryOpKind.GT,
            ast.BinaryOpKind.GE,
        }

        logical_ops = {
            ast.BinaryOpKind.AND,
            ast.BinaryOpKind.OR,
        }

        if node.op == ast.BinaryOpKind.FLOAT_DIV:
            if left_type != "integer":
                raise TypeMismatchError("integer", left_type)
            if right_type != "integer":
                raise TypeMismatchError("integer", right_type)
            node.inferred_type = "integer"
            return "integer"

        if node.op in arithmetic_ops:
            if left_type != "integer":
                raise TypeMismatchError("integer", left_type)
            if right_type != "integer":
                raise TypeMismatchError("integer", right_type)
            node.inferred_type = "integer"
            return "integer"

        if node.op in logical_ops:
            if left_type != "boolean":
                raise TypeMismatchError("boolean", left_type)
            if right_type != "boolean":
                raise TypeMismatchError("boolean", right_type)
            node.inferred_type = "boolean"
            return "boolean"

        if node.op in comparison_ops:
            if left_type != right_type:
                raise TypeMismatchError(left_type, right_type)
            node.inferred_type = "boolean"
            return "boolean"

        raise TypeError(f"Unknown binary operator: {node.op}")