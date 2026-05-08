from __future__ import annotations

import argparse
import subprocess
import sys
import textwrap
from pathlib import Path

from src.pascal.parser import PascalParser, PascalParserError
from src.pascal.semantic import SemanticChecker, IdentScope, SemanticException
from src.codegen.jvm_codegen import JVMCodeGen

SAMPLES_DIR = Path("samples")
OUT_DIR = Path("out")

EXPECTED_ERRORS = {
    "error_if_not_bool.pas",
    "error_redeclare.pas",
    "error_types.pas",
    "error_undefined.pas",
}


def _class_name(path: Path) -> str:
    s = path.stem
    return s[0].upper() + s[1:]


def run_tests(verbose: bool = False, do_run: bool = False):
    OUT_DIR.mkdir(exist_ok=True)

    jasmin_candidates = [Path("jasmin-2.4/jasmin.jar"), Path("tools/jasmin.jar"), Path.home() / "jasmin.jar"]
    jasmin_jar = next((p for p in jasmin_candidates if p.exists()), None)

    samples = sorted(SAMPLES_DIR.glob("*.pas"))
    if not samples:
        print("No .pas files found in samples/")
        return

    passed = failed = skipped = 0

    for pas_file in samples:
        name = pas_file.name
        expected_error = name in EXPECTED_ERRORS
        print(f"\n{'─' * 55}")
        print(f"  {name}")

        text = pas_file.read_text(encoding="utf-8")

        try:
            parser = PascalParser(text)
            program = parser.parse_program()
        except PascalParserError as e:
            if expected_error:
                print(f"  [SKIP] Expected parse error: {e}")
                skipped += 1
            else:
                print(f"  [FAIL] Unexpected parse error: {e}")
                failed += 1
            continue

        checker = SemanticChecker()
        scope = IdentScope()
        try:
            checker.check(program, scope)
        except SemanticException as e:
            if expected_error:
                print(f"  [SKIP] Expected semantic error: {e}")
                skipped += 1
            else:
                print(f"  [FAIL] Unexpected semantic error: {e}")
                failed += 1
            continue

        if expected_error:
            print(f"  [FAIL] Expected an error but analysis passed")
            failed += 1
            continue

        cn = _class_name(pas_file)
        gen = JVMCodeGen(class_name=cn)
        try:
            jasmin_text = gen.generate(program)
        except Exception as e:
            print(f"  [FAIL] Codegen exception: {e}")
            failed += 1
            continue

        j_file = OUT_DIR / f"{cn}.j"
        j_file.write_text(jasmin_text, encoding="utf-8")
        print(f"  [OK]   Generated → {j_file}")

        if verbose:
            print(textwrap.indent(jasmin_text, "       "))

        if jasmin_jar is None:
            if do_run:
                print("  [WARN] jasmin.jar not found — skipping assembly")
            passed += 1
            continue

        asm = subprocess.run(
            ["java", "-jar", str(jasmin_jar), "-d", str(OUT_DIR), str(j_file)],
            capture_output=True, text=True,
        )
        if asm.returncode != 0:
            print(f"  [FAIL] Jasmin error:\n{textwrap.indent(asm.stderr, '         ')}")
            failed += 1
            continue
        print(f"  [OK]   Assembled  → {OUT_DIR}/{cn}.class")

        if do_run:
            run_result = subprocess.run(
                ["java", "-cp", str(OUT_DIR), cn],
                capture_output=True, text=True, timeout=10,
            )
            output = run_result.stdout.strip()
            if run_result.returncode != 0:
                err = run_result.stderr.strip()
                print(f"  [FAIL] Runtime error:\n{textwrap.indent(err, '         ')}")
                failed += 1
                continue
            if output:
                print(f"  [OUT]  {output!r}")
            print(f"  [OK]   Run OK (exit 0)")

        passed += 1

    print(f"\n{'═' * 55}")
    print(f"  Results: {passed} passed, {failed} failed, {skipped} skipped (expected errors)")
    if jasmin_jar is None and not do_run:
        print(
            "\n  Tip: place jasmin.jar in the project root to also assemble .class files.\n"
            "  Download: https://jasmin.sourceforge.net/"
        )
    print()
    return failed == 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Run codegen tests for all .pas samples")
    ap.add_argument("--run",     action="store_true", help="Assemble and run each .class")
    ap.add_argument("--verbose", action="store_true", help="Print generated Jasmin code")
    args = ap.parse_args()
    ok = run_tests(verbose=args.verbose, do_run=args.run)
    sys.exit(0 if ok else 1)