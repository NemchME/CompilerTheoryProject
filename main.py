from pathlib import Path

from src.pascal.parser import PascalParser
from src.ast.builder import dump_ast


def main():
    path = Path("samples/01_minimal.pas")
    text = path.read_text(encoding="utf-8")

    parser = PascalParser(text)
    program = parser.parse_program()

    print(dump_ast(program))


if __name__ == "__main__":
    main()