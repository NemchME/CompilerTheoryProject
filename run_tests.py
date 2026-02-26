from pathlib import Path

from src.pascal.parser import PascalParser, PascalParserError


def main() -> None:
    base = Path("samples")
    files = sorted(base.glob("*.pas"))

    if not files:
        print("No .pas files in samples/tests")
        return

    ok = 0
    bad = 0

    for path in files:
        text = path.read_text(encoding="utf-8")
        try:
            PascalParser(text).parse_program()
            print(f"[OK]    {path.name}")
            ok += 1
        except PascalParserError as e:
            print(f"[ERROR] {path.name}")
            print(str(e))
            print("-" * 40)
            bad += 1

    print(f"\nSummary: OK={ok}, ERROR={bad}, TOTAL={ok+bad}")


if __name__ == "__main__":
    main()
