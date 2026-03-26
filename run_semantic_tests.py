from pathlib import Path

from src.pascal.parser import PascalParser, PascalParserError
from src.pascal.semantic import SemanticChecker, IdentScope, SemanticException


def main():
    base = Path("samples")
    files = sorted(base.glob("*.pas"))

    if not files:
        print("No .pas files in samples")
        return

    ok = 0
    bad = 0

    for path in files:
        text = path.read_text(encoding="utf-8")

        try:
            program = PascalParser(text).parse_program()

            scope = IdentScope()
            checker = SemanticChecker()
            checker.check(program, scope)

            print(f"[OK]    {path.name}")
            ok += 1

        except (PascalParserError, SemanticException) as e:
            print(f"[ERROR] {path.name}")
            print(f"  {e}")
            print("-" * 40)
            bad += 1

    print(f"\nSummary: OK={ok}, ERROR={bad}, TOTAL={ok + bad}")


if __name__ == "__main__":
    main()