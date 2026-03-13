from pathlib import Path

from src.pascal.parser import PascalParser
from src.ast.builder import dump_ast
from src.semantics.analyzer import SemanticAnalyzer
from src.semantics.errors import SemanticError


def main():
    path = Path("samples/01_minimal.pas")
    text = path.read_text(encoding="utf-8")

    parser = PascalParser(text)
    program = parser.parse_program()

    print(dump_ast(program))

    try:
        SemanticAnalyzer().analyze(program)
        print("\nSemantic analysis: OK")
    except SemanticError as e:
        print("\n" + str(e))


if __name__ == "__main__":
    main()