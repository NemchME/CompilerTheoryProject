from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional


class ASTNode:
    pass

@dataclass
class Program(ASTNode):
    name: str
    block: "Block"


@dataclass
class Block(ASTNode):
    var_decls: List["VarDecl"]
    statements: List["Stmt"]


@dataclass
class VarDecl(ASTNode):
    names: List[str]
    type_name: str

class Stmt(ASTNode):
    pass


@dataclass
class Assign(Stmt):
    target: str
    expr: "Expr"


@dataclass
class If(Stmt):
    cond: "Expr"
    then_branch: List[Stmt]
    else_branch: Optional[List[Stmt]]


@dataclass
class While(Stmt):
    cond: "Expr"
    body: List[Stmt]

class Expr(ASTNode):
    pass


@dataclass
class BinOp(Expr):
    op: str
    left: Expr
    right: Expr


@dataclass
class UnOp(Expr):
    op: str
    operand: Expr


@dataclass
class Literal(Expr):
    value: object


@dataclass
class Ident(Expr):
    name: str