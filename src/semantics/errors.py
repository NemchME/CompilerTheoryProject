class SemanticError(Exception):
    pass


class UndefinedVariableError(SemanticError):
    def __init__(self, name: str):
        super().__init__(f"Semantic error: variable '{name}' is not declared")


class DuplicateVariableError(SemanticError):
    def __init__(self, name: str):
        super().__init__(f"Semantic error: variable '{name}' is already declared")


class TypeMismatchError(SemanticError):
    def __init__(self, expected: str, actual: str):
        super().__init__(f"Semantic error: cannot assign {actual} to {expected}")