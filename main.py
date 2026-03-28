from pathlib import Path

from src.pascal.parser import PascalParser
from src.pascal.semantic import SemanticChecker, IdentScope
from src.ast.printer import dump_ast


def main():
    path = Path("samples/function_demo.pas")
    if not path.exists():
        path = Path("samples/minimal.pas")

    text = path.read_text(encoding="utf-8")
    parser = PascalParser(text)
    program = parser.parse_program()

    scope = IdentScope()
    checker = SemanticChecker()

    checker.check(program, scope)
    print(dump_ast(program))

    checker.execute(program)


if __name__ == "__main__":
    main()
