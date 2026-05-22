#!/usr/bin/env python3
"""
Использование:
    python pasc.py <файл.pas>          # скомпилировать и запустить
    python pasc.py <файл.pas> --no-run # только скомпилировать
    python pasc.py <файл.pas> --ast    # показать AST
    python pasc.py <файл.pas> --bytecode # показать Jasmin байт-код
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from src.pascal.parser import PascalParser, PascalParserError
from src.pascal.semantic import SemanticChecker, IdentScope, SemanticException
from src.codegen.jvm_codegen import JVMCodeGen

JASMIN_CANDIDATES = [
    Path("jasmin-2.4/jasmin.jar"),
    Path("jasmin.jar"),
    Path("tools/jasmin.jar"),
]
OUT_DIR = Path("out")
RUNTIME_SRC = Path("PascalRuntime.java")
RUNTIME_CLASS = Path("out/PascalRuntime.class")


def find_jasmin() -> Path | None:
    return next((p for p in JASMIN_CANDIDATES if p.exists()), None)


def class_name_from(path: Path) -> str:
    s = path.stem
    return s[0].upper() + s[1:]


def ensure_runtime():
    if RUNTIME_CLASS.exists():
        return True
    if not RUNTIME_SRC.exists():
        print(f"Ошибка: {RUNTIME_SRC} не найден в корне проекта.")
        return False
    OUT_DIR.mkdir(exist_ok=True)
    result = subprocess.run(
        ["javac", "-d", str(OUT_DIR), str(RUNTIME_SRC)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Ошибка компиляции PascalRuntime.java:\n{result.stderr}")
        return False
    print(f"[OK] Скомпилирован: {RUNTIME_CLASS}")
    return True


def compile_and_run(source: Path, *, show_ast: bool = False, do_run: bool = True, show_bytecode: bool = False):
    if not source.exists():
        print(f"Ошибка: файл не найден: {source}")
        sys.exit(1)
    text = source.read_text(encoding="utf-8")

    try:
        parser = PascalParser(text)
        program = parser.parse_program()
    except PascalParserError as e:
        print(f"Синтаксическая ошибка:\n{e}")
        sys.exit(1)

    checker = SemanticChecker()
    scope = IdentScope()
    try:
        checker.check(program, scope)
    except SemanticException as e:
        print(f"Семантическая ошибка: {e}")
        sys.exit(1)

    if show_ast:
        from src.ast.printer import dump_ast
        print("=== AST ===")
        print(dump_ast(program))

    cn = class_name_from(source)
    gen = JVMCodeGen(class_name=cn)
    jasmin_text = gen.generate(program)

    OUT_DIR.mkdir(exist_ok=True)
    j_file = OUT_DIR / f"{cn}.j"
    j_file.write_text(jasmin_text, encoding="utf-8")
    print(f"[OK] Сгенерирован: {j_file}")

    if show_bytecode:
        print()
        print("=== Jasmin байт-код ===")
        print("─" * 40)
        print(jasmin_text)
        print("─" * 40)

    jasmin_jar = find_jasmin()
    if jasmin_jar is None:
        print("Jasmin не найден.")
        sys.exit(1)

    if not ensure_runtime():
        sys.exit(1)

    asm = subprocess.run(
        ["java", "-jar", str(jasmin_jar), "-d", str(OUT_DIR), str(j_file)],
        capture_output=True, text=True,
    )
    if asm.returncode != 0:
        print(f"Ошибка Jasmin:\n{asm.stderr}")
        sys.exit(1)
    print(f"[OK] Собран:       {OUT_DIR}/{cn}.class")

    if do_run:
        print(f"Результат работы {cn}:")
        print("─" * 40)
        subprocess.run(["java", "-cp", str(OUT_DIR), cn])
        print("─" * 40)


def main():
    ap = argparse.ArgumentParser(
        prog="pasc",
        description="Pascal -> JVM компилятор",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("source", help="Pascal исходный файл (.pas)")
    ap.add_argument("--ast",    action="store_true", help="Показать AST")
    ap.add_argument("--no-run",   action="store_true", help="Не запускать после сборки")
    ap.add_argument("--bytecode", action="store_true", help="Показать сгенерированный Jasmin байт-код")
    args = ap.parse_args()

    compile_and_run(
        Path(args.source),
        show_ast=args.ast,
        do_run=not args.no_run,
        show_bytecode=args.bytecode,
    )


if __name__ == "__main__":
    main()