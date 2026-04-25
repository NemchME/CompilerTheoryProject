from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class ASTNode:
    row: int | None = None
    col: int | None = None
    node_type = None
    node_ident = None


class Stmt(ASTNode):
    pass


class Expr(ASTNode):
    pass


class BinaryOpKind(Enum):
    ADD = "+"
    SUB = "-"
    MUL = "*"
    FLOAT_DIV = "/"
    INT_DIV = "div"
    MOD = "mod"
    AND = "and"
    OR = "or"
    EQ = "="
    NE = "<>"
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="


class UnaryOpKind(Enum):
    PLUS = "+"
    MINUS = "-"
    NOT = "not"


@dataclass
class Ident(Expr):
    name: str


@dataclass
class Literal(Expr):
    value: object


@dataclass
class BinOp(Expr):
    op: BinaryOpKind
    left: Expr
    right: Expr


@dataclass
class UnOp(Expr):
    op: UnaryOpKind
    expr: Expr

@dataclass
class Cast(Expr):
    type_name: str
    expr: Expr

@dataclass
class VarDecl(ASTNode):
    ident: Ident
    type_name: str


@dataclass
class CompoundStmt(Stmt):
    statements: List[Stmt]

@dataclass
class Call(Expr, Stmt):
    func: Ident
    args: list[Expr]

@dataclass
class Assign(Stmt):
    ident: Ident
    expr: Expr


@dataclass
class If(Stmt):
    cond: Expr
    then_branch: CompoundStmt
    else_branch: Optional[CompoundStmt]


@dataclass
class While(Stmt):
    cond: Expr
    body: CompoundStmt


@dataclass
class For(Stmt):
    ident: Ident
    start: Expr
    direction: str
    end: Expr
    body: CompoundStmt


@dataclass
class Break(Stmt):
    pass


@dataclass
class Continue(Stmt):
    pass

@dataclass
class Block(ASTNode):
    var_decls: List[VarDecl]
    func_decls: List["Func"] = field(default_factory=list)
    body: CompoundStmt = field(default_factory=lambda: CompoundStmt([]))


@dataclass
class Program(ASTNode):
    name: str
    block: Block

@dataclass
class TypeConvertNode(Expr):
    expr: Expr
    target_type: object
    node_type: object = None

@dataclass
class Func(ASTNode):
    name: Ident
    params: List[VarDecl]
    return_type: str
    block: Block


@dataclass
class Return(Stmt):
    expr: Optional[Expr]