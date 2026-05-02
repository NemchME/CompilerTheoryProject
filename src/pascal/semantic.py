from __future__ import annotations
from enum import Enum
from src.ast import nodes as ast


class BaseType(Enum):
    INT = "int"
    BOOL = "bool"
    STR = "string"
    VOID = "void"
    DOUBLE = "double"

    def __str__(self):
        return self.value


class TypeDesc:
    def __init__(self, base_type=None, return_type=None, params=None):
        self.base_type = base_type
        self.return_type = return_type
        self.params = list(params or [])

    @property
    def is_func(self):
        return self.return_type is not None

    def __eq__(self, other):
        if other is None:
            return False
        if self.is_func != other.is_func:
            return False
        if not self.is_func:
            return self.base_type == other.base_type
        return self.return_type == other.return_type and self.params == other.params

    def __str__(self):
        if not self.is_func:
            return str(self.base_type)
        return f"{self.return_type}({', '.join(map(str, self.params))})"


INT = TypeDesc(BaseType.INT)
BOOL = TypeDesc(BaseType.BOOL)
STR = TypeDesc(BaseType.STR)
VOID = TypeDesc(BaseType.VOID)
DOUBLE = TypeDesc(BaseType.DOUBLE)


class IdentDesc:
    _counters: dict = {}

    @classmethod
    def _next_num(cls, category: str) -> int:
        cls._counters[category] = cls._counters.get(category, 0) + 1
        return cls._counters[category]

    @classmethod
    def reset_counters(cls):
        cls._counters.clear()

    def __init__(self, name, type_, scope_type="global"):
        self.name = name
        self.type = type_
        self.scope_type = scope_type
        self.built_in = False
        self.value = None
        self.func_node = None
        self.num = IdentDesc._next_num(scope_type) if not self.built_in else 0

    def __str__(self):
        if self.built_in:
            return f"{self.name}: {self.type} [built-in]"
        category_label = {
            "global": "глобальная",
            "local":  "локальная",
            "param":  "параметр",
            "func":   "функция",
        }.get(self.scope_type, self.scope_type)
        return f"{self.name}: {self.type} [{category_label} #{self.num}]"


class IdentScope:
    def __init__(self, parent=None, current_func=None):
        self.parent = parent
        self.idents = {}
        self.current_func = current_func

    def add_ident(self, ident: IdentDesc):
        if ident.name in self.idents:
            raise SemanticException(f"Повторное объявление {ident.name}")
        self.idents[ident.name] = ident
        return ident

    def get_ident(self, name: str):
        scope = self
        while scope:
            if name in scope.idents:
                return scope.idents[name]
            scope = scope.parent
        return None


class SemanticException(Exception):
    pass


class _SignalBreak(Exception):
    pass


class _SignalContinue(Exception):
    pass


class _SignalReturn(Exception):
    def __init__(self, value):
        self.value = value


class SemanticChecker:
    def __init__(self):
        self.global_scope = None
        self.call_stack = []
        self.output = []

    def check(self, node, scope: IdentScope):
        if self.global_scope is None:
            self.global_scope = scope
            IdentDesc.reset_counters()
            self._add_builtins(scope)
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

    @staticmethod
    def _type_from_name(name: str):
        if name == "integer":
            return INT
        if name == "boolean":
            return BOOL
        if name == "char":
            return STR
        if name == "double":
            return DOUBLE
        raise SemanticException(f"Неизвестный тип {name}")

    def _add_builtins(self, scope: IdentScope):
        for name in ("write", "writeln"):
            ident = IdentDesc.__new__(IdentDesc)
            ident.name = name
            ident.type = TypeDesc(return_type=VOID, params=[])
            ident.scope_type = "global"
            ident.built_in = True
            ident.value = None
            ident.func_node = None
            ident.num = 0
            scope.add_ident(ident)
        for name in ("read", "readln"):
            ident = IdentDesc.__new__(IdentDesc)
            ident.name = name
            ident.type = TypeDesc(return_type=VOID, params=[])
            ident.scope_type = "global"
            ident.built_in = True
            ident.value = None
            ident.func_node = None
            ident.num = 0
            scope.add_ident(ident)

    def visit_Program(self, node: ast.Program, scope):
        self.check(node.block, scope)
        node.node_type = VOID

    def visit_Literal(self, node: ast.Literal, scope):
        if isinstance(node.value, bool):
            node.node_type = BOOL
        elif isinstance(node.value, float):
            node.node_type = DOUBLE
        elif isinstance(node.value, int):
            node.node_type = INT
        elif isinstance(node.value, str):
            node.node_type = STR

    def visit_Ident(self, node: ast.Ident, scope):
        ident = scope.get_ident(node.name)
        if ident is None:
            raise SemanticException(f"Переменная {node.name} не объявлена")
        node.node_type = ident.type
        node.node_ident = ident

    def visit_VarDecl(self, node: ast.VarDecl, scope):
        type_ = self._type_from_name(node.type_name)
        scope_type = "local" if scope.current_func else "global"
        desc = scope.add_ident(IdentDesc(node.ident.name, type_, scope_type))
        node.node_type = type_
        node.node_ident = desc
        node.ident.node_type = type_
        node.ident.node_ident = desc

    def visit_Assign(self, node: ast.Assign, scope):
        self.check(node.ident, scope)
        self.check(node.expr, scope)
        if node.ident.node_type != node.expr.node_type:
            node.expr = ast.TypeConvertNode(node.expr, node.ident.node_type, node.ident.node_type)
            node.expr.row = getattr(node.expr.expr, 'row', None)
            node.expr.col = getattr(node.expr.expr, 'col', None)
        node.node_type = node.ident.node_type

    def visit_UnOp(self, node: ast.UnOp, scope):
        self.check(node.expr, scope)
        expr_type = node.expr.node_type
        if node.op == ast.UnaryOpKind.NOT:
            if expr_type != BOOL:
                raise SemanticException("not требует boolean")
            node.node_type = BOOL
        else:
            if expr_type != INT:
                raise SemanticException("Унарный + и - требуют integer")
            node.node_type = INT

    def visit_BinOp(self, node: ast.BinOp, scope):
        self.check(node.left, scope)
        self.check(node.right, scope)
        left = node.left.node_type
        right = node.right.node_type
        op = node.op
        if op in {ast.BinaryOpKind.ADD, ast.BinaryOpKind.SUB, ast.BinaryOpKind.MUL, ast.BinaryOpKind.INT_DIV, ast.BinaryOpKind.MOD, ast.BinaryOpKind.FLOAT_DIV}:
            if left == right and left == INT:
                node.node_type = INT
            elif left == right and left == DOUBLE:
                node.node_type = DOUBLE
            elif op == ast.BinaryOpKind.FLOAT_DIV and {left, right} <= {INT, DOUBLE}:
                node.node_type = DOUBLE
            else:
                raise SemanticException("Арифметика требует integer или double")
        elif op in {ast.BinaryOpKind.EQ, ast.BinaryOpKind.NE, ast.BinaryOpKind.LT, ast.BinaryOpKind.LE, ast.BinaryOpKind.GT, ast.BinaryOpKind.GE}:
            if left == right:
                node.node_type = BOOL
            else:
                raise SemanticException("Несовместимые типы в сравнении")
        elif op in {ast.BinaryOpKind.AND, ast.BinaryOpKind.OR}:
            if left == BOOL and right == BOOL:
                node.node_type = BOOL
            else:
                raise SemanticException("Логика требует bool")
        else:
            raise SemanticException(f"Неизвестная операция {op}")

    def visit_If(self, node: ast.If, scope):
        self.check(node.cond, scope)
        if node.cond.node_type != BOOL:
            raise SemanticException("Условие должно быть bool")
        self.check(node.then_branch, IdentScope(scope, current_func=scope.current_func))
        if node.else_branch:
            self.check(node.else_branch, IdentScope(scope, current_func=scope.current_func))

    def visit_While(self, node: ast.While, scope):
        self.check(node.cond, scope)
        if node.cond.node_type != BOOL:
            raise SemanticException("Условие должно быть bool")
        self.check(node.body, IdentScope(scope, current_func=scope.current_func))

    def visit_For(self, node: ast.For, scope):
        loop_scope = IdentScope(scope, current_func=scope.current_func)
        ident = loop_scope.add_ident(IdentDesc(node.ident.name, INT, "local"))
        node.ident.node_type = INT
        node.ident.node_ident = ident
        self.check(node.start, loop_scope)
        self.check(node.end, loop_scope)
        if node.start.node_type != INT or node.end.node_type != INT:
            raise SemanticException("Границы for должны быть integer")
        self.check(node.body, loop_scope)

    def visit_Block(self, node: ast.Block, scope):
        block_scope = IdentScope(scope, current_func=scope.current_func)
        for decl in node.var_decls:
            self.check(decl, block_scope)
        for func in node.func_decls:
            self._register_func(func, block_scope)
        for func in node.func_decls:
            self.check(func, block_scope)
        self.check(node.body, block_scope)

    def visit_CompoundStmt(self, node: ast.CompoundStmt, scope):
        local_scope = IdentScope(scope, current_func=scope.current_func)
        for stmt in node.statements:
            self.check(stmt, local_scope)
        node.node_type = VOID

    def _register_func(self, node: ast.Func, scope: IdentScope):
        ret_type = self._type_from_name(node.return_type)
        param_types = [self._type_from_name(param.type_name) for param in node.params]
        ident = IdentDesc(node.name.name, TypeDesc(return_type=ret_type, params=param_types), "func")
        ident.func_node = node
        scope.add_ident(ident)
        node.name.node_ident = ident
        node.name.node_type = ident.type
        node.node_ident = ident
        node.node_type = ident.type

    def visit_Func(self, node: ast.Func, scope):
        ret_type = self._type_from_name(node.return_type)
        func_scope = IdentScope(scope, current_func=node)
        for param in node.params:
            type_ = self._type_from_name(param.type_name)
            desc = IdentDesc(param.ident.name, type_, "param")
            func_scope.add_ident(desc)
            param.node_type = type_
            param.node_ident = desc
            param.ident.node_type = type_
            param.ident.node_ident = desc
        self.check(node.block, func_scope)
        has_return = self._block_has_return(node.block)
        if ret_type != VOID and not has_return:
            raise SemanticException(f"В функции {node.name.name} нет return")

    def _block_has_return(self, block: ast.Block):
        return self._compound_has_return(block.body)

    def _compound_has_return(self, compound: ast.CompoundStmt):
        for stmt in compound.statements:
            if isinstance(stmt, ast.Return):
                return True
            if isinstance(stmt, ast.If):
                if self._compound_has_return(stmt.then_branch):
                    return True
                if stmt.else_branch and self._compound_has_return(stmt.else_branch):
                    return True
            if isinstance(stmt, (ast.While, ast.For)) and self._compound_has_return(stmt.body):
                return True
        return False

    def visit_Cast(self, node: ast.Cast, scope):
        self.check(node.expr, scope)
        target = self._type_from_name(node.type_name)
        node.node_type = target

    def visit_Return(self, node: ast.Return, scope):
        if scope.current_func is None:
            raise SemanticException("return можно использовать только внутри функции")
        expected_type = self._type_from_name(scope.current_func.return_type)
        if node.expr is None:
            if expected_type != VOID:
                raise SemanticException("Функция должна возвращать значение")
            node.node_type = VOID
            return
        self.check(node.expr, scope)
        if node.expr.node_type != expected_type:
            node.expr = ast.TypeConvertNode(node.expr, expected_type, expected_type)
            node.expr.row = getattr(node.expr.expr, 'row', None)
            node.expr.col = getattr(node.expr.expr, 'col', None)
        node.node_type = expected_type

    def visit_Call(self, node: ast.Call, scope):
        ident = scope.get_ident(node.func.name)
        if ident is None:
            raise SemanticException(f"Функция {node.func.name} не объявлена")
        if not ident.type.is_func:
            raise SemanticException(f"{node.func.name} не является функцией")
        for arg in node.args:
            self.check(arg, scope)
        if not ident.built_in and len(node.args) != len(ident.type.params):
            raise SemanticException("Неверное количество аргументов")
        if not ident.built_in:
            for i, (arg, expected_type) in enumerate(zip(node.args, ident.type.params)):
                if arg.node_type != expected_type:
                    node.args[i] = ast.TypeConvertNode(arg, expected_type, expected_type)
                    node.args[i].row = getattr(arg, 'row', None)
                    node.args[i].col = getattr(arg, 'col', None)
        node.func.node_ident = ident
        node.func.node_type = ident.type
        node.node_ident = ident
        node.node_type = ident.type.return_type

    def execute(self, program: ast.Program):
        if self.global_scope is None:
            scope = IdentScope()
            self.check(program, scope)
        env = self._make_frame(None)
        self._exec_block(program.block, env)
        return env

    def _make_frame(self, parent):
        return {"__parent__": parent}

    def _declare_var(self, frame, name, value=None):
        frame[name] = value

    def _lookup_frame(self, frame, name):
        curr = frame
        while curr is not None:
            if name in curr:
                return curr
            curr = curr.get("__parent__")
        return None

    def _get_var(self, frame, name):
        found = self._lookup_frame(frame, name)
        if found is None:
            raise SemanticException(f"Переменная {name} не объявлена")
        return found[name]

    def _set_var(self, frame, name, value):
        found = self._lookup_frame(frame, name)
        if found is None:
            frame[name] = value
        else:
            found[name] = value

    def _default_value(self, type_name: str):
        if type_name == "integer":
            return 0
        if type_name == "boolean":
            return False
        if type_name == "char":
            return ''
        if type_name == "double":
            return 0.0
        return None

    def _exec_block(self, block: ast.Block, frame):
        for decl in block.var_decls:
            self._declare_var(frame, decl.ident.name, self._default_value(decl.type_name))
        for func in block.func_decls:
            frame[func.name.name] = func
        self._exec_compound(block.body, frame)

    def _exec_compound(self, compound: ast.CompoundStmt, frame):
        local = self._make_frame(frame)
        for stmt in compound.statements:
            self._exec_stmt(stmt, local)

    def _exec_stmt(self, node, frame):
        if isinstance(node, ast.CompoundStmt):
            self._exec_compound(node, frame)
            return
        if isinstance(node, ast.Assign):
            self._set_var(frame, node.ident.name, self._eval_expr(node.expr, frame))
            return
        if isinstance(node, ast.If):
            if self._eval_expr(node.cond, frame):
                self._exec_compound(node.then_branch, frame)
            elif node.else_branch is not None:
                self._exec_compound(node.else_branch, frame)
            return
        if isinstance(node, ast.While):
            while self._eval_expr(node.cond, frame):
                try:
                    self._exec_compound(node.body, frame)
                except _SignalContinue:
                    continue
                except _SignalBreak:
                    break
            return
        if isinstance(node, ast.For):
            start = self._eval_expr(node.start, frame)
            end = self._eval_expr(node.end, frame)
            loop_frame = self._make_frame(frame)
            self._declare_var(loop_frame, node.ident.name, start)
            step = 1 if node.direction == "to" else -1
            def cond(v):
                return v <= end if step == 1 else v >= end
            while cond(self._get_var(loop_frame, node.ident.name)):
                try:
                    self._exec_compound(node.body, loop_frame)
                except _SignalContinue:
                    pass
                except _SignalBreak:
                    break
                self._set_var(loop_frame, node.ident.name, self._get_var(loop_frame, node.ident.name) + step)
            return
        if isinstance(node, ast.Break):
            raise _SignalBreak()
        if isinstance(node, ast.Continue):
            raise _SignalContinue()
        if isinstance(node, ast.Return):
            value = self._eval_expr(node.expr, frame) if node.expr is not None else None
            raise _SignalReturn(value)
        if isinstance(node, ast.Call):
            self._eval_call(node, frame)
            return
        raise SemanticException(f"Не умею выполнять {type(node).__name__}")

    def _eval_expr(self, node, frame):
        if isinstance(node, ast.Literal):
            return node.value
        if isinstance(node, ast.Ident):
            return self._get_var(frame, node.name)
        if isinstance(node, ast.TypeConvertNode):
            value = self._eval_expr(node.expr, frame)
            return self._convert_value(value, node.target_type)
        if isinstance(node, ast.UnOp):
            value = self._eval_expr(node.expr, frame)
            if node.op == ast.UnaryOpKind.NOT:
                return not value
            if node.op == ast.UnaryOpKind.PLUS:
                return +value
            return -value
        if isinstance(node, ast.BinOp):
            left = self._eval_expr(node.left, frame)
            right = self._eval_expr(node.right, frame)
            op = node.op
            if op == ast.BinaryOpKind.ADD:
                return left + right
            if op == ast.BinaryOpKind.SUB:
                return left - right
            if op == ast.BinaryOpKind.MUL:
                return left * right
            if op in (ast.BinaryOpKind.FLOAT_DIV, ast.BinaryOpKind.INT_DIV):
                return left // right
            if op == ast.BinaryOpKind.MOD:
                return left % right
            if op == ast.BinaryOpKind.AND:
                return left and right
            if op == ast.BinaryOpKind.OR:
                return left or right
            if op == ast.BinaryOpKind.EQ:
                return left == right
            if op == ast.BinaryOpKind.NE:
                return left != right
            if op == ast.BinaryOpKind.LT:
                return left < right
            if op == ast.BinaryOpKind.LE:
                return left <= right
            if op == ast.BinaryOpKind.GT:
                return left > right
            if op == ast.BinaryOpKind.GE:
                return left >= right
        if isinstance(node, ast.Cast):
            value = self._eval_expr(node.expr, frame)
            return self._convert_value(value, self._type_from_name(node.type_name))
        if isinstance(node, ast.Call):
            return self._eval_call(node, frame)
        raise SemanticException(f"Не умею вычислять {type(node).__name__}")

    def _convert_value(self, value, target_type):
        if target_type == INT:
            return int(value)
        if target_type == BOOL:
            return bool(value)
        if target_type == DOUBLE:
            return float(value)
        if target_type == STR:
            text = str(value)
            return text[:1] if text else ''
        return value

    def _eval_call(self, node: ast.Call, frame):
        name = node.func.name
        args = [self._eval_expr(arg, frame) for arg in node.args]
        if name == "write":
            text = ''.join(str(arg) for arg in args)
            self.output.append(text)
            print(text, end='')
            return None
        if name == "writeln":
            text = ''.join(str(arg) for arg in args)
            self.output.append(text + "\n")
            print(text)
            return None
        if name in ("read", "readln"):
            return None
        func_node = self._get_var(frame, name)
        if not isinstance(func_node, ast.Func):
            raise SemanticException(f"{name} не является функцией")
        if len(args) != len(func_node.params):
            raise SemanticException("Неверное количество аргументов")
        call_frame = self._make_frame(frame)
        for param, arg_value in zip(func_node.params, args):
            self._declare_var(call_frame, param.ident.name, arg_value)
        self.call_stack.append(name)
        try:
            self._exec_block(func_node.block, call_frame)
        except _SignalReturn as signal:
            self.call_stack.pop()
            return signal.value
        self.call_stack.pop()
        return None