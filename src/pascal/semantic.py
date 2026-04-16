from __future__ import annotations
from enum import Enum
from src.ast import nodes as ast
import warnings


class BaseType(Enum):
    INT = "int"
    FLOAT = "double"
    BOOL = "bool"
    STR = "string"
    VOID = "void"


class TypeDesc:
    def __init__(self, base_type=None, return_type=None, params=None):
        self.base_type = base_type
        self.return_type = return_type
        self.params = list(params or [])

    def __eq__(self, other):
        return isinstance(other, TypeDesc) and self.base_type == other.base_type


INT = TypeDesc(BaseType.INT)
FLOAT = TypeDesc(BaseType.FLOAT)
BOOL = TypeDesc(BaseType.BOOL)
STR = TypeDesc(BaseType.STR)
VOID = TypeDesc(BaseType.VOID)


class IdentDesc:
    def __init__(self, name, type_, scope_type="global", index=0):
        self.name = name
        self.type = type_
        self.scope_type = scope_type
        self.index = index


class IdentScope:
    def __init__(self, parent=None, current_func=None):
        self.parent = parent
        self.idents = {}
        self.current_func = current_func

    def add_ident(self, ident):
        if ident.name in self.idents:
            raise Exception(f"Повторное объявление {ident.name}")
        self.idents[ident.name] = ident
        return ident

    def get_ident(self, name):
        scope = self
        while scope:
            if name in scope.idents:
                return scope.idents[name]
            scope = scope.parent
        return None


class SemanticException(Exception):
    pass


class SemanticChecker:

    def __init__(self):
        self.global_scope = None
        self._register_builtins()

    def _register_builtins(self):
        self.builtins = {
            'write': TypeDesc(return_type=VOID, params=[]),
            'writeln': TypeDesc(return_type=VOID, params=[]),
            'read': TypeDesc(return_type=VOID, params=[]),
            'readln': TypeDesc(return_type=VOID, params=[]),
        }

    def _try_convert(self, expr, from_type, to_type, scope):
        if from_type.base_type == to_type.base_type:
            return expr

        if from_type.base_type == BaseType.INT and to_type.base_type == BaseType.FLOAT:
            return ast.TypeConvertNode(expr, FLOAT, FLOAT)

        if from_type.base_type == BaseType.FLOAT and to_type.base_type == BaseType.INT:
            warnings.warn(
                f"Преобразование double в int может привести к потере точности "
                f"(строка {getattr(expr, 'row', '?')})"
            )
            return ast.TypeConvertNode(expr, INT, INT)

        return None

    def check(self, node, scope):
        if self.global_scope is None:
            self.global_scope = scope
            for name, type_desc in self.builtins.items():
                if scope.get_ident(name) is None:
                    scope.add_ident(IdentDesc(name, type_desc, "builtin", 0))
        method = f"visit_{type(node).__name__}"
        return getattr(self, method, self.generic_visit)(node, scope)

    def generic_visit(self, node, scope):
        for attr in vars(node).values():
            if isinstance(attr, list):
                for item in attr:
                    if hasattr(item, "__dict__"):
                        self.check(item, scope)
            elif hasattr(attr, "__dict__"):
                self.check(attr, scope)

    def _type_from_name(self, name):
        if name == "integer":
            return INT
        if name == "boolean":
            return BOOL
        if name == "char":
            return STR
        if name == "double":
            return FLOAT
        raise SemanticException(f"Неизвестный тип {name}")

    def visit_Literal(self, node, scope):
        if isinstance(node.value, int):
            node.node_type = INT
        elif isinstance(node.value, bool):
            node.node_type = BOOL
        elif isinstance(node.value, str):
            node.node_type = STR

    def visit_Ident(self, node, scope):
        ident = scope.get_ident(node.name)
        if ident is None:
            raise SemanticException(f"Переменная {node.name} не объявлена")
        node.node_type = ident.type
        node.node_ident = ident

    def visit_VarDecl(self, node, scope):
        type_ = self._type_from_name(node.type_name)

        if scope.current_func:
            scope_type = "variable"
            index = len([i for i in scope.idents.values() if i.scope_type == "variable"])
        else:
            scope_type = "global"
            index = 0

        desc = scope.add_ident(IdentDesc(node.ident.name, type_, scope_type, index))

        node.node_type = type_
        node.ident.node_type = type_
        node.ident.node_ident = desc

    def visit_Block(self, node, scope):
        local_scope = IdentScope(scope, current_func=scope.current_func)

        for func in node.func_decls:
            ret = self._type_from_name(func.return_type)
            params = [self._type_from_name(p.type_name) for p in func.params]
            desc = IdentDesc(func.name.name, TypeDesc(return_type=ret, params=params))
            local_scope.add_ident(desc)
            func.node_ident = desc

        for decl in node.var_decls:
            self.check(decl, local_scope)

        for func in node.func_decls:
            self.check(func, local_scope)

        self.check(node.body, local_scope)

    def visit_Func(self, node, scope):
        func_scope = IdentScope(scope, current_func=node)

        for i, param in enumerate(node.params):
            type_ = self._type_from_name(param.type_name)
            desc = IdentDesc(param.ident.name, type_, "param", i)
            func_scope.add_ident(desc)

            param.node_ident = desc
            param.ident.node_ident = desc
            param.ident.node_type = type_
            param.node_type = type_

        self.check(node.block, func_scope)

    def visit_Call(self, node, scope):
        ident = scope.get_ident(node.func.name)
        if ident is None:
            raise SemanticException(f"Функция {node.func.name} не объявлена")

        for arg in node.args:
            self.check(arg, scope)

        if ident.scope_type == "builtin":
            node.node_type = VOID
            return

        expected_params = ident.type.params
        if len(node.args) != len(expected_params):
            raise SemanticException(
                f"Функция {node.func.name} ожидает {len(expected_params)} аргументов, "
                f"получено {len(node.args)}"
            )

        for i, (arg, expected_type) in enumerate(zip(node.args, expected_params)):
            converted = self._try_convert(arg, arg.node_type, expected_type, scope)
            if converted:
                node.args[i] = converted
            elif arg.node_type.base_type != expected_type.base_type:
                raise SemanticException(
                    f"Аргумент {i + 1} функции {node.func.name} имеет неверный тип: "
                    f"ожидается {expected_type.base_type.value}, получено {arg.node_type.base_type.value}"
                )

        node.node_type = ident.type.return_type

    def visit_Assign(self, node, scope):
        self.check(node.ident, scope)
        self.check(node.expr, scope)

        left_type = node.ident.node_type
        right_type = node.expr.node_type

        if left_type.base_type != right_type.base_type:
            converted = self._try_convert(node.expr, right_type, left_type, scope)
            if converted:
                node.expr = converted
            else:
                raise SemanticException(
                    f"Несовместимые типы в присваивании: {left_type.base_type.value} := {right_type.base_type.value}"
                )

    def visit_BinOp(self, node, scope):
        self.check(node.left, scope)
        self.check(node.right, scope)

        l = node.left.node_type.base_type
        r = node.right.node_type.base_type

        op_kind = node.op

        if op_kind in (ast.BinaryOpKind.AND, ast.BinaryOpKind.OR):
            if l != BaseType.BOOL or r != BaseType.BOOL:
                raise SemanticException("Логические операции требуют boolean операндов")
            node.node_type = BOOL
            return

        if op_kind in (ast.BinaryOpKind.EQ, ast.BinaryOpKind.NE,
                       ast.BinaryOpKind.LT, ast.BinaryOpKind.LE,
                       ast.BinaryOpKind.GT, ast.BinaryOpKind.GE):
            if l == BaseType.INT and r == BaseType.FLOAT:
                node.left = ast.TypeConvertNode(node.left, FLOAT, FLOAT)
            elif l == BaseType.FLOAT and r == BaseType.INT:
                node.right = ast.TypeConvertNode(node.right, FLOAT, FLOAT)
            node.node_type = BOOL
            return

        if l == BaseType.INT and r == BaseType.INT:
            if op_kind == ast.BinaryOpKind.FLOAT_DIV:
                node.node_type = FLOAT
            else:
                node.node_type = INT
        elif l == BaseType.FLOAT and r == BaseType.FLOAT:
            node.node_type = FLOAT
        elif l == BaseType.INT and r == BaseType.FLOAT:
            node.left = ast.TypeConvertNode(node.left, FLOAT, FLOAT)
            node.node_type = FLOAT
        elif l == BaseType.FLOAT and r == BaseType.INT:
            node.right = ast.TypeConvertNode(node.right, FLOAT, FLOAT)
            node.node_type = FLOAT
        elif l == BaseType.STR and r == BaseType.STR and op_kind == ast.BinaryOpKind.ADD:
            node.node_type = STR
        else:
            raise SemanticException(f"Несовместимые типы в бинарной операции: {l.value} и {r.value}")

    def visit_UnOp(self, node, scope):
        self.check(node.expr, scope)
        t = node.expr.node_type.base_type

        if node.op == ast.UnaryOpKind.NOT:
            if t != BaseType.BOOL:
                raise SemanticException("not требует boolean")
            node.node_type = BOOL
        elif node.op in (ast.UnaryOpKind.PLUS, ast.UnaryOpKind.MINUS):
            if t not in (BaseType.INT, BaseType.FLOAT):
                raise SemanticException("Унарный +/- требует число")
            node.node_type = node.expr.node_type
        else:
            raise SemanticException("Неизвестная унарная операция")

    def visit_If(self, node, scope):
        self.check(node.cond, scope)
        if node.cond.node_type.base_type != BaseType.BOOL:
            raise SemanticException("Условие if должно быть boolean")
        self.check(node.then_branch, scope)
        if node.else_branch:
            self.check(node.else_branch, scope)

    def visit_While(self, node, scope):
        self.check(node.cond, scope)
        if node.cond.node_type.base_type != BaseType.BOOL:
            raise SemanticException("Условие while должно быть boolean")
        self.check(node.body, scope)

    def visit_For(self, node, scope):
        self.check(node.ident, scope)
        self.check(node.start, scope)
        self.check(node.end, scope)
        if node.ident.node_type.base_type != BaseType.INT:
            raise SemanticException("Счётчик for должен быть integer")
        if node.start.node_type.base_type != BaseType.INT:
            raise SemanticException("Начальное значение for должно быть integer")
        if node.end.node_type.base_type != BaseType.INT:
            raise SemanticException("Конечное значение for должно быть integer")
        self.check(node.body, scope)

    def visit_Return(self, node, scope):
        if node.expr:
            self.check(node.expr, scope)
            current_func = scope.current_func
            if current_func:
                expected_type = self._type_from_name(current_func.return_type)
                actual_type = node.expr.node_type

                if expected_type.base_type != actual_type.base_type:
                    converted = self._try_convert(node.expr, actual_type, expected_type, scope)
                    if converted:
                        node.expr = converted
                    else:
                        raise SemanticException(
                            f"Неверный тип возврата: ожидается {expected_type.base_type.value}, "
                            f"получено {actual_type.base_type.value}"
                        )

    def visit_TypeConvertNode(self, node, scope):
        self.check(node.expr, scope)
        node.node_type = node.target_type

    def visit_CompoundStmt(self, node, scope):
        for stmt in node.statements:
            self.check(stmt, scope)

    def visit_Program(self, node, scope):
        self.check(node.block, scope)

    def visit_Break(self, node, scope):
        pass

    def visit_Continue(self, node, scope):
        pass

    def execute(self, node):
        pass