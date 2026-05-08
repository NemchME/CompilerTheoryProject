from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from src.pascal.parser import PascalParser, PascalParserError
from src.pascal.semantic import SemanticChecker, IdentScope, SemanticException
from src.ast.printer import dump_ast
from src.codegen.jvm_codegen import JVMCodeGen


def _derive_class_name(source_path: Path) -> str:
    stem = source_path.stem
    return stem[0].upper() + stem[1:] if stem else "Program"


def compile_file(
    source_path: Path,
    *,
    print_ast: bool = True,
    do_codegen: bool = True,
    do_run: bool = False,
    out_dir: Path = Path("out"),
):
    try:
        text = source_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: file not found: {source_path}", file=sys.stderr)
        sys.exit(1)

    try:
        parser = PascalParser(text)
        program = parser.parse_program()
    except PascalParserError as e:
        print(f"Syntax error:\n{e}", file=sys.stderr)
        sys.exit(1)

    checker = SemanticChecker()
    scope = IdentScope()
    try:
        checker.check(program, scope)
    except SemanticException as e:
        print(f"Semantic error: {e}", file=sys.stderr)
        sys.exit(1)

    if print_ast:
        print("=== AST ===")
        print(dump_ast(program), end="")
        print()

    if not do_codegen:
        return

    class_name = _derive_class_name(source_path)
    gen = JVMCodeGen(class_name=class_name)
    jasmin_text = gen.generate(program)

    out_dir.mkdir(parents=True, exist_ok=True)
    j_file = out_dir / f"{class_name}.j"
    j_file.write_text(jasmin_text, encoding="utf-8")
    print(f"Generated Jasmin file: {j_file}")

    if do_run:
        _assemble_and_run(j_file, class_name, out_dir)


def _assemble_and_run(j_file: Path, class_name: str, out_dir: Path):
    jasmin_candidates = [
        Path("jasmin.jar"),
        Path("tools/jasmin.jar"),
        Path.home() / "jasmin.jar",
    ]
    jasmin_jar = next((p for p in jasmin_candidates if p.exists()), None)

    if jasmin_jar is None:
        print(
            "\nTo assemble and run, place jasmin.jar next to main.py.\n"
            "Download: https://jasmin.sourceforge.net/\n\n"
            f"Then run manually:\n"
            f"  java -jar jasmin.jar -d {out_dir} {j_file}\n"
            f"  java -cp {out_dir} {class_name}",
            file=sys.stderr,
        )
        return

    print(f"Assembling {j_file} ...")
    result = subprocess.run(
        ["java", "-jar", str(jasmin_jar), "-d", str(out_dir), str(j_file)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print("Jasmin error:\n" + result.stderr, file=sys.stderr)
        return
    print("Assembly OK.")

    print(f"Running {class_name} ...\n{'─' * 40}")
    subprocess.run(["java", "-cp", str(out_dir), class_name])
    print(f"{'─' * 40}")


def main():
    ap = argparse.ArgumentParser(description="Pascal subset → JVM bytecode compiler")
    ap.add_argument("source", nargs="?", help="Pascal source file (.pas)")
    ap.add_argument("--ast",        dest="ast",     action="store_true",  default=True)
    ap.add_argument("--no-ast",     dest="ast",     action="store_false")
    ap.add_argument("--codegen",    dest="codegen", action="store_true",  default=True)
    ap.add_argument("--no-codegen", dest="codegen", action="store_false")
    ap.add_argument("--run",        dest="run",     action="store_true",  default=False)
    ap.add_argument("--no-run",     dest="run",     action="store_false")
    ap.add_argument("--out", default="out", help="Output directory (default: out)")
    args = ap.parse_args()

    if args.source is None:
        for candidate in ("samples/function_demo.pas", "samples/minimal.pas"):
            if Path(candidate).exists():
                args.source = candidate
                break
        else:
            ap.print_help()
            sys.exit(0)

    compile_file(
        Path(args.source),
        print_ast=args.ast,
        do_codegen=args.codegen,
        do_run=args.run,
        out_dir=Path(args.out),
    )


if __name__ == "__main__":
    main()