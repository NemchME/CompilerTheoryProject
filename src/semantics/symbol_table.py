from dataclasses import dataclass


@dataclass
class Symbol:
    name: str


@dataclass
class BuiltinTypeSymbol(Symbol):
    pass


@dataclass
class VarSymbol(Symbol):
    type_name: str


class SymbolTable:
    def __init__(self):
        self._symbols: dict[str, Symbol] = {}
        self.define(BuiltinTypeSymbol("integer"))
        self.define(BuiltinTypeSymbol("char"))
        self.define(BuiltinTypeSymbol("boolean"))

    def define(self, symbol: Symbol) -> None:
        self._symbols[symbol.name] = symbol

    def lookup(self, name: str):
        return self._symbols.get(name)

    def has_in_current_scope(self, name: str) -> bool:
        return name in self._symbols