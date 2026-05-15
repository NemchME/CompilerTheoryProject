from __future__ import annotations
from src.ast import nodes as ast
from src.pascal.semantic import (
    BaseType, TypeDesc, INT, BOOL, STR, VOID, DOUBLE,
)

def _jvm_type(type_desc: TypeDesc | None) -> str:
    if type_desc is None:
        return "V"
    if type_desc.is_func:
        return _jvm_type(type_desc.return_type)
    bt = type_desc.base_type
    if bt == BaseType.INT:
        return "I"
    if bt == BaseType.BOOL:
        return "I"
    if bt == BaseType.STR:
        return "Ljava/lang/String;"
    if bt == BaseType.VOID:
        return "V"
    if bt == BaseType.DOUBLE:
        return "D"
    return "I"


def _pascal_type_to_jvm_field(type_name: str) -> str:
    mapping = {
        "integer": "I",
        "boolean": "I",
        "char":    "Ljava/lang/String;",
        "double":  "D",
    }
    return mapping.get(type_name, "I")


def _node_is_double(node: ast.ASTNode) -> bool:
    t = getattr(node, 'node_type', None)
    if t is None:
        return False
    if isinstance(t, TypeDesc):
        return t.base_type == BaseType.DOUBLE
    return False


def _node_is_string(node: ast.ASTNode) -> bool:
    t = getattr(node, 'node_type', None)
    if t is None:
        return False
    if isinstance(t, TypeDesc):
        return t == STR
    return False


class _LabelCounter:
    def __init__(self):
        self._n = 0

    def next(self, prefix: str = "L") -> str:
        self._n += 1
        return f"{prefix}{self._n}"


class _LocalVarTable:
    def __init__(self, start_slot: int = 0):
        self._table: dict[str, tuple[int, str]] = {}
        # имя -> (номер слота, тип)
        self._next_slot = start_slot

    def declare(self, name: str, type_name: str) -> int:
        slot = self._next_slot
        self._table[name] = (slot, type_name)
        self._next_slot += 2 if type_name == "double" else 1
        return slot

    def slot(self, name: str) -> int:
        return self._table[name][0]

    def type_name(self, name: str) -> str:
        return self._table[name][1]

    def has(self, name: str) -> bool:
        return name in self._table


class JVMCodeGen:
    def __init__(self, class_name: str = "Program"):
        self._class_name = class_name
        self._lines: list[str] = []
        self._labels = _LabelCounter()
        self._loop_stack: list[tuple[str, str]] = []
        self._locals: _LocalVarTable | None = None
        self._globals: set[str] = set()
        # имя глобальной переменной -> тип
        self._global_types: dict[str, str] = {}
        self._in_function = False

    def generate(self, program: ast.Program) -> str:
        self._lines = []
        self._labels = _LabelCounter()
        self._collect_globals(program.block)
        self._emit_class_header(program.name)
        self._emit_all_fields(program.block)
        self._emit_clinit()
        for func in program.block.func_decls:
            self._emit_function(func)
        self._emit_main(program.block)
        return "\n".join(self._lines) + "\n"

    def _collect_globals(self, block: ast.Block):
        for decl in block.var_decls:
            self._globals.add(decl.ident.name)
            self._global_types[decl.ident.name] = decl.type_name

    def _emit_class_header(self, program_name: str):
        cn = self._class_name
        self._emit(f".class public {cn}")
        self._emit(f".super java/lang/Object")
        self._emit("")

    def _emit_all_fields(self, block: ast.Block):
        self._emit(f".field static _scanner Ljava/util/Scanner;")
        for decl in block.var_decls:
            jvm_t = _pascal_type_to_jvm_field(decl.type_name)
            self._emit(f".field static {decl.ident.name} {jvm_t}")
        self._emit("")

    def _emit_clinit(self):
        cn = self._class_name
        self._emit(".method static <clinit>()V")
        self._emit("    .limit stack 3")
        self._emit("    .limit locals 0")
        self._emit("    new java/util/Scanner")
        self._emit("    dup")
        self._emit("    getstatic java/lang/System/in Ljava/io/InputStream;")
        self._emit(f"    invokespecial java/util/Scanner/<init>(Ljava/io/InputStream;)V")
        self._emit(f"    putstatic {cn}/_scanner Ljava/util/Scanner;")
        self._emit("    return")
        self._emit(".end method")
        self._emit("")

    def _emit_function(self, func: ast.Func):
        self._in_function = True
        ret_jvm = _pascal_type_to_jvm_field(func.return_type)
        params_jvm = "".join(_pascal_type_to_jvm_field(p.type_name) for p in func.params)
        descriptor = f"({params_jvm}){ret_jvm}"
        self._emit(f".method public static {func.name.name}{descriptor}")
        self._emit(f"    .limit stack 16")
        lv = _LocalVarTable(start_slot=0)
        for param in func.params:
            lv.declare(param.ident.name, param.type_name)
        for decl in func.block.var_decls:
            lv.declare(decl.ident.name, decl.type_name)
        self._emit(f"    .limit locals {max(lv._next_slot + 16, 1)}")
        self._locals = lv
        for decl in func.block.var_decls:
            self._emit_default_value(decl.type_name)
            self._emit_store(lv.slot(decl.ident.name), decl.type_name)
        self._emit_compound(func.block.body)
        self._emit_default_value(func.return_type)
        self._emit_return_for_type(func.return_type)
        self._emit(".end method")
        self._emit("")
        self._in_function = False
        self._locals = None

    def _emit_main(self, block: ast.Block):
        self._emit(".method public static main([Ljava/lang/String;)V")
        self._emit("    .limit stack 16")
        lv = _LocalVarTable(start_slot=1)
        for decl in block.var_decls:
            lv.declare(decl.ident.name, decl.type_name)
        self._emit(f"    .limit locals {max(lv._next_slot + 16, 2)}")
        self._locals = lv
        self._in_function = False
        for decl in block.var_decls:
            self._emit_default_value(decl.type_name)
            self._emit_store(lv.slot(decl.ident.name), decl.type_name)
        self._emit_compound(block.body)
        self._emit("    return")
        self._emit(".end method")

    def _emit_stmt(self, node: ast.ASTNode):
        if isinstance(node, ast.CompoundStmt):
            self._emit_compound(node)
        elif isinstance(node, ast.Assign):
            self._emit_assign(node)
        elif isinstance(node, ast.If):
            self._emit_if(node)
        elif isinstance(node, ast.While):
            self._emit_while(node)
        elif isinstance(node, ast.For):
            self._emit_for(node)
        elif isinstance(node, ast.Break):
            self._emit_break()
        elif isinstance(node, ast.Continue):
            self._emit_continue()
        elif isinstance(node, ast.Return):
            self._emit_return(node)
        elif isinstance(node, ast.Call):
            self._emit_call_stmt(node)

    def _emit_compound(self, node: ast.CompoundStmt):
        for stmt in node.statements:
            self._emit_stmt(stmt)

    def _emit_assign(self, node: ast.Assign):
        self._emit_expr(node.expr)
        name = node.ident.name
        if self._locals and self._locals.has(name):
            type_name = self._locals.type_name(name)
            self._emit_store(self._locals.slot(name), type_name)
        elif name in self._globals:
            type_name = self._global_types[name]
            jvm_t = _pascal_type_to_jvm_field(type_name)
            self._emit(f"    putstatic {self._class_name}/{name} {jvm_t}")
        else:
            self._emit("    istore 0")

    def _emit_if(self, node: ast.If):
        self._emit_expr(node.cond)
        if node.else_branch:
            else_label = self._labels.next("ELSE")
            end_label = self._labels.next("ENDIF")
            self._emit(f"    ifeq {else_label}")
            self._emit_compound(node.then_branch)
            self._emit(f"    goto {end_label}")
            self._emit(f"{else_label}:")
            self._emit_compound(node.else_branch)
            self._emit(f"{end_label}:")
        else:
            end_label = self._labels.next("ENDIF")
            self._emit(f"    ifeq {end_label}")
            self._emit_compound(node.then_branch)
            self._emit(f"{end_label}:")

    def _emit_while(self, node: ast.While):
        loop_start = self._labels.next("WHILE_START")
        loop_end = self._labels.next("WHILE_END")
        self._loop_stack.append((loop_end, loop_start))
        self._emit(f"{loop_start}:")
        self._emit_expr(node.cond)
        self._emit(f"    ifeq {loop_end}")
        self._emit_compound(node.body)
        self._emit(f"    goto {loop_start}")
        self._emit(f"{loop_end}:")
        self._loop_stack.pop()

    def _emit_for(self, node: ast.For):
        loop_start = self._labels.next("FOR_START")
        loop_end = self._labels.next("FOR_END")
        loop_cont = self._labels.next("FOR_CONT")
        step = 1 if node.direction == "to" else -1
        self._emit_expr(node.start)
        name = node.ident.name
        type_name = "integer"
        if self._locals and self._locals.has(name):
            slot = self._locals.slot(name)
        else:
            slot = self._locals.declare(name, type_name) if self._locals else 2
        end_slot = self._locals.declare(f"__for_end_{loop_start}", type_name) if self._locals else slot + 1
        self._emit_store(slot, type_name)
        self._emit_expr(node.end)
        self._emit_store(end_slot, type_name)
        self._loop_stack.append((loop_end, loop_cont))
        self._emit(f"{loop_start}:")
        self._emit_load(slot, type_name)
        self._emit_load(end_slot, type_name)
        if node.direction == "to":
            self._emit(f"    if_icmpgt {loop_end}")
        else:
            self._emit(f"    if_icmplt {loop_end}")
        self._emit_compound(node.body)
        self._emit(f"{loop_cont}:")
        self._emit_load(slot, type_name)
        self._emit(f"    ldc {step}")
        self._emit("    iadd")
        self._emit_store(slot, type_name)
        self._emit(f"    goto {loop_start}")
        self._emit(f"{loop_end}:")
        self._loop_stack.pop()

    def _emit_break(self):
        if self._loop_stack:
            break_label, _ = self._loop_stack[-1]
            self._emit(f"    goto {break_label}")

    def _emit_continue(self):
        if self._loop_stack:
            _, cont_label = self._loop_stack[-1]
            self._emit(f"    goto {cont_label}")

    def _emit_return(self, node: ast.Return):
        if node.expr is not None:
            self._emit_expr(node.expr)
            t = getattr(node.expr, 'node_type', None)
            if t == STR:
                self._emit("    areturn")
            elif _node_is_double(node.expr):
                self._emit("    dreturn")
            else:
                self._emit("    ireturn")
        else:
            self._emit("    return")

    def _emit_call_stmt(self, node: ast.Call):
        name = node.func.name
        if name in ("write", "writeln"):
            self._emit_io_write(node, newline=(name == "writeln"))
        elif name in ("read", "readln"):
            self._emit_io_read(node)
        else:
            self._emit_call_expr(node)
            ret_type = getattr(node, 'node_type', None)
            if ret_type is not None and ret_type != VOID:
                if _node_is_double(node):
                    self._emit("    pop2")
                else:
                    self._emit("    pop")

    def _emit_io_write(self, node: ast.Call, newline: bool):
        method = "println" if newline else "print"
        for arg in node.args:
            self._emit("    getstatic java/lang/System/out Ljava/io/PrintStream;")
            self._emit_expr(arg)
            t = getattr(arg, 'node_type', None)
            if t == STR:
                self._emit(f"    invokevirtual java/io/PrintStream/{method}(Ljava/lang/String;)V")
            elif _node_is_double(arg):
                self._emit(f"    invokevirtual java/io/PrintStream/{method}(D)V")
            else:
                self._emit(f"    invokevirtual java/io/PrintStream/{method}(I)V")
        if newline and not node.args:
            self._emit("    getstatic java/lang/System/out Ljava/io/PrintStream;")
            self._emit(f"    invokevirtual java/io/PrintStream/{method}()V")

    def _emit_io_read(self, node: ast.Call):
        for arg in node.args:
            if not isinstance(arg, ast.Ident):
                continue
            name = arg.name
            if self._locals and self._locals.has(name):
                type_name = self._locals.type_name(name)
            elif name in self._globals:
                type_name = self._global_types[name]
            else:
                continue
            self._emit(f"    getstatic {self._class_name}/_scanner Ljava/util/Scanner;")
            if type_name == "double":
                self._emit("    invokevirtual java/util/Scanner/nextDouble()D")
            elif type_name == "char":
                self._emit("    invokevirtual java/util/Scanner/next()Ljava/lang/String;")
            else:
                self._emit("    invokevirtual java/util/Scanner/nextInt()I")
            if self._locals and self._locals.has(name):
                self._emit_store(self._locals.slot(name), type_name)
            else:
                jvm_t = _pascal_type_to_jvm_field(type_name)
                self._emit(f"    putstatic {self._class_name}/{name} {jvm_t}")

    def _emit_expr(self, node: ast.ASTNode):
        if isinstance(node, ast.Literal):
            self._emit_literal(node)
        elif isinstance(node, ast.Ident):
            self._emit_ident_load(node)
        elif isinstance(node, ast.BinOp):
            self._emit_binop(node)
        elif isinstance(node, ast.UnOp):
            self._emit_unop(node)
        elif isinstance(node, ast.TypeConvertNode):
            self._emit_typeconvert(node)
        elif isinstance(node, ast.Cast):
            self._emit_cast(node)
        elif isinstance(node, ast.Call):
            self._emit_call_expr(node)
        else:
            self._emit("    iconst_0")

    def _emit_literal(self, node: ast.Literal):
        v = node.value
        if isinstance(v, bool):
            self._emit("    iconst_1" if v else "    iconst_0")
        elif isinstance(v, float):
            self._emit(f"    ldc2_w {v}")
        elif isinstance(v, int):
            self._emit_int_const(v)
        elif isinstance(v, str):
            self._emit(f'    ldc "{v}"')
        else:
            self._emit("    iconst_0")

    def _emit_int_const(self, v: int):
        if -1 <= v <= 5:
            self._emit(f"    iconst_{v}" if v >= 0 else "    iconst_m1") # Однобайтовая инструкция
        elif -128 <= v <= 127:
            self._emit(f"    bipush {v}")
        elif -32768 <= v <= 32767:
            self._emit(f"    sipush {v}")
        else:
            self._emit(f"    ldc {v}")

    def _emit_ident_load(self, node: ast.Ident):
        name = node.name
        if self._locals and self._locals.has(name):
            slot = self._locals.slot(name)
            type_name = self._locals.type_name(name)
            self._emit_load(slot, type_name)
        elif name in self._globals:
            type_name = self._global_types[name]
            jvm_t = _pascal_type_to_jvm_field(type_name)
            self._emit(f"    getstatic {self._class_name}/{name} {jvm_t}")
        else:
            self._emit("    iconst_0")

    def _emit_binop(self, node: ast.BinOp):
        op = node.op
        is_double = _node_is_double(node.left) or _node_is_double(node.right)
        cmp_ops = {
            ast.BinaryOpKind.EQ, ast.BinaryOpKind.NE,
            ast.BinaryOpKind.LT, ast.BinaryOpKind.LE,
            ast.BinaryOpKind.GT, ast.BinaryOpKind.GE,
        }
        if op in cmp_ops:
            self._emit_comparison(node, is_double)
            return
        if op == ast.BinaryOpKind.AND:
            self._emit_logical_and(node)
            return
        if op == ast.BinaryOpKind.OR:
            self._emit_logical_or(node)
            return
        self._emit_expr(node.left)
        self._emit_expr(node.right)
        prefix = "d" if is_double else "i"
        if op == ast.BinaryOpKind.ADD:
            self._emit(f"    {prefix}add")
        elif op == ast.BinaryOpKind.SUB:
            self._emit(f"    {prefix}sub")
        elif op == ast.BinaryOpKind.MUL:
            self._emit(f"    {prefix}mul")
        elif op == ast.BinaryOpKind.FLOAT_DIV:
            self._emit(f"    {prefix}div")
        elif op == ast.BinaryOpKind.INT_DIV:
            self._emit("    idiv")
        elif op == ast.BinaryOpKind.MOD:
            self._emit("    irem")

    def _emit_comparison(self, node: ast.BinOp, is_double: bool):
        self._emit_expr(node.left)
        self._emit_expr(node.right)
        true_label = self._labels.next("CMP_TRUE")
        end_label = self._labels.next("CMP_END")
        op = node.op
        if is_double:
            self._emit("    dcmpg")
            branch = {
                ast.BinaryOpKind.EQ: f"    ifeq {true_label}",
                ast.BinaryOpKind.NE: f"    ifne {true_label}",
                ast.BinaryOpKind.LT: f"    iflt {true_label}",
                ast.BinaryOpKind.LE: f"    ifle {true_label}",
                ast.BinaryOpKind.GT: f"    ifgt {true_label}",
                ast.BinaryOpKind.GE: f"    ifge {true_label}",
            }[op]
        else:
            branch = {
                ast.BinaryOpKind.EQ: f"    if_icmpeq {true_label}",
                ast.BinaryOpKind.NE: f"    if_icmpne {true_label}",
                ast.BinaryOpKind.LT: f"    if_icmplt {true_label}",
                ast.BinaryOpKind.LE: f"    if_icmple {true_label}",
                ast.BinaryOpKind.GT: f"    if_icmpgt {true_label}",
                ast.BinaryOpKind.GE: f"    if_icmpge {true_label}",
            }[op]
        self._emit(branch)
        self._emit("    iconst_0")
        self._emit(f"    goto {end_label}")
        self._emit(f"{true_label}:")
        self._emit("    iconst_1")
        self._emit(f"{end_label}:")

    def _emit_logical_and(self, node: ast.BinOp):
        false_label = self._labels.next("AND_FALSE")
        end_label = self._labels.next("AND_END")
        self._emit_expr(node.left)
        self._emit(f"    ifeq {false_label}")
        self._emit_expr(node.right)
        self._emit(f"    ifeq {false_label}")
        self._emit("    iconst_1")
        self._emit(f"    goto {end_label}")
        self._emit(f"{false_label}:")
        self._emit("    iconst_0")
        self._emit(f"{end_label}:")

    def _emit_logical_or(self, node: ast.BinOp):
        true_label = self._labels.next("OR_TRUE")
        end_label = self._labels.next("OR_END")
        self._emit_expr(node.left)
        self._emit(f"    ifne {true_label}")
        self._emit_expr(node.right)
        self._emit(f"    ifne {true_label}")
        self._emit("    iconst_0")
        self._emit(f"    goto {end_label}")
        self._emit(f"{true_label}:")
        self._emit("    iconst_1")
        self._emit(f"{end_label}:")

    def _emit_unop(self, node: ast.UnOp):
        self._emit_expr(node.expr)
        is_double = _node_is_double(node.expr)
        if node.op == ast.UnaryOpKind.MINUS:
            self._emit("    dneg" if is_double else "    ineg")
        elif node.op == ast.UnaryOpKind.PLUS:
            pass
        elif node.op == ast.UnaryOpKind.NOT:
            self._emit("    iconst_1")
            self._emit("    ixor")

    def _emit_typeconvert(self, node: ast.TypeConvertNode):
        self._emit_expr(node.expr)
        src = getattr(node.expr, 'node_type', None)
        tgt = node.target_type
        src_is_double = _node_is_double(node.expr) or (
            isinstance(src, TypeDesc) and src.base_type == BaseType.DOUBLE)
        tgt_is_double = isinstance(tgt, TypeDesc) and tgt.base_type == BaseType.DOUBLE
        if src_is_double and not tgt_is_double and tgt != STR:
            self._emit("    d2i")
        elif not src_is_double and tgt_is_double and src != STR:
            self._emit("    i2d")

    def _emit_cast(self, node: ast.Cast):
        self._emit_expr(node.expr)
        src_is_double = _node_is_double(node.expr)
        if node.type_name == "double" and not src_is_double:
            self._emit("    i2d")
        elif node.type_name == "integer" and src_is_double:
            self._emit("    d2i")

    def _emit_call_expr(self, node: ast.Call):
        name = node.func.name
        if name in ("write", "writeln"):
            self._emit_io_write(node, newline=(name == "writeln"))
            self._emit("    iconst_0")
            return
        if name in ("read", "readln"):
            self._emit_io_read(node)
            self._emit("    iconst_0")
            return
        ident = getattr(node.func, 'node_ident', None)
        if ident is None:
            return
        for arg in node.args:
            self._emit_expr(arg)
        func_node = getattr(ident, 'func_node', None)
        if func_node:
            params_jvm = "".join(_pascal_type_to_jvm_field(p.type_name) for p in func_node.params)
            ret_jvm = _pascal_type_to_jvm_field(func_node.return_type)
        else:
            param_types = getattr(ident.type, 'params', [])
            params_jvm = "".join(_jvm_type(p) for p in param_types)
            ret_jvm = _jvm_type(ident.type.return_type) if ident.type.return_type else "V"
        descriptor = f"({params_jvm}){ret_jvm}"
        self._emit(f"    invokestatic {self._class_name}/{name}{descriptor}")

    def _emit_load(self, slot: int, type_name: str):
        if type_name == "double":
            self._emit(f"    dload {slot}")
        elif type_name == "char":
            self._emit(f"    aload {slot}")
        else:
            self._emit(f"    iload {slot}")

    def _emit_store(self, slot: int, type_name: str):
        if type_name == "double":
            self._emit(f"    dstore {slot}")
        elif type_name == "char":
            self._emit(f"    astore {slot}")
        else:
            self._emit(f"    istore {slot}")

    def _emit_default_value(self, type_name: str):
        if type_name == "double":
            self._emit("    dconst_0")
        elif type_name == "char":
            self._emit('    ldc ""')
        else:
            self._emit("    iconst_0")

    def _emit_return_for_type(self, type_name: str):
        if type_name == "double":
            self._emit("    dreturn")
        elif type_name == "char":
            self._emit("    areturn")
        elif type_name in ("integer", "boolean"):
            self._emit("    ireturn")
        else:
            self._emit("    return")

    def _emit(self, line: str):
        self._lines.append(line)