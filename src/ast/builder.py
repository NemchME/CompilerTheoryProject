from __future__ import annotations
from typing import Any
from src.ast import nodes as ast


def _label(node: Any) -> str:
    if node is None:
        return "None"
    if isinstance(node, ast.Program):
        return f"Program {node.name}"
    if isinstance(node, ast.Block):
        return "Block"
    if isinstance(node, ast.CompoundStmt):
        return "CompoundStmt"
    if isinstance(node, ast.VarDecl):
        return f"VarDecl {node.ident.name} : {node.type_name}"
    if isinstance(node, ast.Assign):
        return f"Assign {node.ident.name}"
    if isinstance(node, ast.If):
        return "If"
    if isinstance(node, ast.While):
        return "While"
    if isinstance(node, ast.For):
        return f"For {node.ident.name} {node.direction}"
    if isinstance(node, ast.Break):
        return "Break"
    if isinstance(node, ast.Continue):
        return "Continue"
    if isinstance(node, ast.Call):
        return f"Call {node.func.name}"
    if isinstance(node, ast.BinOp):
        return f"BinOp {node.op.value}"
    if isinstance(node, ast.UnOp):
        return f"UnOp {node.op.value}"
    if isinstance(node, ast.Ident):
        return f"Ident {node.name}"
    if isinstance(node, ast.Literal):
        return f"Literal {node.value!r}"
    if isinstance(node, list):
        return f"List[{len(node)}]"
    return type(node).__name__


def _children(node: Any) -> list[Any]:
    if node is None:
        return []
    if isinstance(node, ast.Program):
        return [node.block]
    if isinstance(node, ast.Block):
        return [*node.var_decls, node.body]
    if isinstance(node, ast.CompoundStmt):
        return node.statements
    if isinstance(node, ast.VarDecl):
        return []
    if isinstance(node, ast.Assign):
        return [node.expr]
    if isinstance(node, ast.If):
        parts = [node.cond, node.then_branch]
        if node.else_branch is not None:
            parts.append(node.else_branch)
        return parts
    if isinstance(node, ast.While):
        return [node.cond, node.body]
    if isinstance(node, ast.For):
        return [node.start, node.end, node.body]
    if isinstance(node, ast.Call):
        return node.args
    if isinstance(node, ast.BinOp):
        return [node.left, node.right]
    if isinstance(node, ast.UnOp):
        return [node.expr]
    if isinstance(node, list):
        return list(node)
    return []


def dump_ast(node: Any, indent: str = "", is_last: bool = True) -> str:
    branch = "└─" if is_last else "├─"
    line = indent + branch + _label(node) + "\n"
    children = _children(node)
    next_indent = indent + ("  " if is_last else "│ ")
    for index, child in enumerate(children):
        line += dump_ast(child, next_indent, index == len(children) - 1)
    return line
