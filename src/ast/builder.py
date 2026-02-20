from __future__ import annotations
from dataclasses import is_dataclass, fields
from typing import Any

from src.ast.nodes import ASTNode


def dump_ast(node: Any, indent: str = "", is_last: bool = True) -> str:
    branch = "└─" if is_last else "├─"
    if node is None:
        return indent + branch + "None\n"

    if isinstance(node, (str, int, bool, float)):
        return indent + branch + repr(node) + "\n"

    if isinstance(node, list):
        s = indent + branch + f"List[{len(node)}]\n"
        new_indent = indent + ("  " if is_last else "│ ")
        for idx, item in enumerate(node):
            s += dump_ast(item, new_indent, idx == len(node) - 1)
        return s

    name = type(node).__name__
    s = indent + branch + name + "\n"
    new_indent = indent + ("  " if is_last else "│ ")

    if is_dataclass(node):
        fs = fields(node)
        for idx, f in enumerate(fs):
            val = getattr(node, f.name)
            last_field = idx == len(fs) - 1
            s += new_indent + ("└─" if last_field else "├─") + f"{f.name}\n"
            s += dump_ast(val, new_indent + ("  " if last_field else "│ "), True)
        return s

    return s + new_indent + "└─" + repr(node) + "\n"