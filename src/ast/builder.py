from typing import Any


def node_label(node):
    t = type(node).__name__

    if t == "Program":
        return f"Program {node.name}"

    if t == "Ident":
        return f"Ident {node.name}"

    if t == "Literal":
        return f"Literal {node.value}"

    if t == "BinOp":
        return f"BinOp {node.op.value}"

    if t == "UnOp":
        return f"UnOp {node.op.value}"

    if t == "VarDecl":
        return f"VarDecl {node.ident.name} : {node.type_name}"

    return t


def children(node):
    t = type(node).__name__

    if t == "Program":
        return [node.block]

    if t == "Block":
        return node.var_decls + [node.body]

    if t == "CompoundStmt":
        return node.statements

    if t == "Assign":
        return [node.target, node.value]

    if t == "If":
        c = [node.cond, node.then_branch]
        if node.else_branch:
            c.append(node.else_branch)
        return c

    if t == "While":
        return [node.cond, node.body]

    if t == "For":
        return [node.var, node.start, node.end, node.body]

    if t == "BinOp":
        return [node.left, node.right]

    if t == "UnOp":
        return [node.operand]

    return []


def dump_ast(node: Any, indent: str = "", last: bool = True) -> str:
    branch = "└─" if last else "├─"

    s = indent + branch + node_label(node) + "\n"

    new_indent = indent + ("  " if last else "│ ")

    ch = children(node)

    for i, c in enumerate(ch):
        s += dump_ast(c, new_indent, i == len(ch) - 1)

    return s