from pathlib import Path

from src.pascal.parser import PascalParser
from src.ast.builder import dump_ast
from src.pascal.semantic import SemanticChecker, IdentScope


def main():
    path = Path("samples/minimal.pas")
    text = path.read_text(encoding="utf-8")

    parser = PascalParser(text)
    program = parser.parse_program()

    scope = IdentScope()
    checker = SemanticChecker()

    checker.check(program, scope)

    print(dump_ast(program))


if __name__ == "__main__":
    main()