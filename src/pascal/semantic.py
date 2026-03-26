from enum import Enum
from src.ast import nodes as ast


class BaseType(Enum):
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    STR = "string"
    VOID = "void"

    def __str__(self):
        return self.value


class TypeDesc:
    def __init__(self, base_type=None, return_type=None, params=None):
        self.base_type = base_type
        self.return_type = return_type
        self.params = params or []

    @property
    def is_func(self):
        return self.return_type is not None

    def __eq__(self, other):
        if self.is_func != other.is_func:
            return False

        if not self.is_func:
            return self.base_type == other.base_type

        return (
            self.return_type == other.return_type and
            self.params == other.params
        )

    def __str__(self):
        if not self.is_func:
            return str(self.base_type)

        return f"{self.return_type}({', '.join(map(str, self.params))})"


class IdentDesc:
    def __init__(self, name, type_, scope_type="global"):
        self.name = name
        self.type = type_
        self.scope_type = scope_type


class IdentScope:
    def __init__(self, parent=None):
        self.parent = parent
        self.idents = {}

    def add_ident(self, ident: IdentDesc):
        if ident.name in self.idents:
            raise SemanticException(f"Повторное объявление {ident.name}")

        self.idents[ident.name] = ident

    def get_ident(self, name: str):
        scope = self

        while scope:
            if name in scope.idents:
                return scope.idents[name]
            scope = scope.parent

        return None


class SemanticException(Exception):
    def __init__(self, message):
        super().__init__(message)


class TypeConvert:
    def __init__(self, expr, target_type):
        self.expr = expr
        self.target_type = target_type
        self.node_type = target_type


class SemanticChecker:

    def check(self, node, scope: IdentScope):
        method = f"visit_{type(node).__name__}"
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, scope)

    def generic_visit(self, node, scope):
        for attr in vars(node).values():
            if isinstance(attr, list):
                for item in attr:
                    if hasattr(item, "__dict__"):
                        self.check(item, scope)
            elif hasattr(attr, "__dict__"):
                self.check(attr, scope)


    def visit_Literal(self, node: ast.Literal, scope):
        if isinstance(node.value, bool):
            node.node_type = TypeDesc(BaseType.BOOL)
        elif isinstance(node.value, int):
            node.node_type = TypeDesc(BaseType.INT)
        elif isinstance(node.value, str):
            node.node_type = TypeDesc(BaseType.STR)


    def visit_Ident(self, node: ast.Ident, scope):
        ident = scope.get_ident(node.name)

        if ident is None:
            raise SemanticException(f"Переменная {node.name} не объявлена")

        node.node_type = ident.type
        node.node_ident = ident


    def visit_VarDecl(self, node: ast.VarDecl, scope):
        if node.type_name == "integer":
            type_ = TypeDesc(BaseType.INT)
        elif node.type_name == "boolean":
            type_ = TypeDesc(BaseType.BOOL)
        elif node.type_name == "char":
            type_ = TypeDesc(BaseType.STR)
        else:
            raise SemanticException(f"Неизвестный тип {node.type_name}")

        scope_type = "local" if scope.parent else "global"

        scope.add_ident(IdentDesc(node.ident.name, type_, scope_type))
        node.node_type = type_


    def visit_Assign(self, node: ast.Assign, scope):
        self.check(node.ident, scope)
        self.check(node.expr, scope)

        if node.ident.node_type != node.expr.node_type:
            node.expr = TypeConvert(node.expr, node.ident.node_type)

        node.node_type = node.ident.node_type

    def visit_BinOp(self, node: ast.BinOp, scope):
        self.check(node.left, scope)
        self.check(node.right, scope)

        left = node.left.node_type
        right = node.right.node_type
        op = node.op

        # арифметика
        if op in {
            ast.BinaryOpKind.ADD,
            ast.BinaryOpKind.SUB,
            ast.BinaryOpKind.MUL,
            ast.BinaryOpKind.INT_DIV,
            ast.BinaryOpKind.MOD,
        }:
            if left == right and left.base_type == BaseType.INT:
                node.node_type = left
            else:
                raise SemanticException("Арифметика требует integer")

        elif op in {
            ast.BinaryOpKind.EQ,
            ast.BinaryOpKind.NE,
            ast.BinaryOpKind.LT,
            ast.BinaryOpKind.LE,
            ast.BinaryOpKind.GT,
            ast.BinaryOpKind.GE,
        }:
            if left == right:
                node.node_type = TypeDesc(BaseType.BOOL)
            else:
                raise SemanticException("Несовместимые типы в сравнении")

        elif op in {
            ast.BinaryOpKind.AND,
            ast.BinaryOpKind.OR,
        }:
            if left.base_type == BaseType.BOOL and right.base_type == BaseType.BOOL:
                node.node_type = TypeDesc(BaseType.BOOL)
            else:
                raise SemanticException("Логика требует bool")

        else:
            raise SemanticException(f"Неизвестная операция {op}")


    def visit_If(self, node: ast.If, scope):
        self.check(node.cond, scope)

        if node.cond.node_type.base_type != BaseType.BOOL:
            raise SemanticException("Условие должно быть bool")

        self.check(node.then_branch, IdentScope(scope))

        if node.else_branch:
            self.check(node.else_branch, IdentScope(scope))


    def visit_While(self, node: ast.While, scope):
        self.check(node.cond, scope)

        if node.cond.node_type.base_type != BaseType.BOOL:
            raise SemanticException("Условие должно быть bool")

        self.check(node.body, IdentScope(scope))


    def visit_For(self, node: ast.For, scope):
        loop_scope = IdentScope(scope)

        ident = IdentDesc(node.ident.name, TypeDesc(BaseType.INT), "local")
        loop_scope.add_ident(ident)

        self.check(node.start, loop_scope)
        self.check(node.end, loop_scope)
        self.check(node.body, loop_scope)


    def visit_Block(self, node: ast.Block, scope):
        block_scope = IdentScope(scope)

        for decl in node.var_decls:
            self.check(decl, block_scope)

        self.check(node.body, block_scope)


    def visit_CompoundStmt(self, node: ast.CompoundStmt, scope):
        local_scope = IdentScope(scope)

        for stmt in node.statements:
            self.check(stmt, local_scope)


    def visit_Func(self, node: ast.Func, scope):
        if node.return_type == "integer":
            ret_type = TypeDesc(BaseType.INT)
        elif node.return_type == "boolean":
            ret_type = TypeDesc(BaseType.BOOL)
        elif node.return_type == "char":
            ret_type = TypeDesc(BaseType.STR)
        else:
            raise SemanticException(f"Неизвестный тип {node.return_type}")

        param_types = []
        for param in node.params:
            if param.type_name == "integer":
                param_types.append(TypeDesc(BaseType.INT))
            elif param.type_name == "boolean":
                param_types.append(TypeDesc(BaseType.BOOL))
            elif param.type_name == "char":
                param_types.append(TypeDesc(BaseType.STR))
            else:
                raise SemanticException(f"Неизвестный тип {param.type_name}")

        func_type = TypeDesc(return_type=ret_type, params=param_types)

        scope.add_ident(IdentDesc(node.name.name, func_type, "global"))

        func_scope = IdentScope(scope)

        for param, ptype in zip(node.params, param_types):
            func_scope.add_ident(IdentDesc(param.ident.name, ptype, "param"))

        self.check(node.body, func_scope)


    def visit_Return(self, node: ast.Return, scope):
        if node.expr:
            self.check(node.expr, scope)
            node.node_type = node.expr.node_type
        else:
            node.node_type = TypeDesc(BaseType.VOID)


    def visit_Call(self, node: ast.Call, scope):
        ident = scope.get_ident(node.func.name)

        if ident is None:
            raise SemanticException(f"Функция {node.func.name} не объявлена")

        if not ident.type.is_func:
            raise SemanticException(f"{node.func.name} не является функцией")

        if len(node.args) != len(ident.type.params):
            raise SemanticException("Неверное количество аргументов")

        for i, (arg, expected_type) in enumerate(zip(node.args, ident.type.params)):
            self.check(arg, scope)

            if arg.node_type != expected_type:
                node.args[i] = TypeConvert(arg, expected_type)

        node.node_type = ident.type.return_type