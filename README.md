# Генерация JVM байт-кода (Jasmin)


Генератор кода расположен в `src/codegen/jvm_codegen.py` и реализует полный обход AST-дерева после семантического анализа.

---

## Архитектура кодогенератора

```
src/
├── ast/
│   ├── nodes.py          # AST-узлы
│   └── printer.py        # Печать AST
├── pascal/
│   ├── parser.py         # Парсер Lark → AST 
│   └── semantic.py       # Семантический анализ (добавлена поддержка double)
└── codegen/
    ├── __init__.py
    └── jvm_codegen.py    # Генератор JVM байт-кода (Jasmin)
```

---

## Соответствие типов Pascal → JVM

| Тип Pascal | JVM-дескриптор | Инструкции         |
|-----------|----------------|--------------------|
| `integer` | `I`            | `iload/istore/iadd/…` |
| `double`  | `D`            | `dload/dstore/dadd/…` |
| `boolean` | `I`            | `iload/istore`, 0=false 1=true |
| `char`    | `Ljava/lang/String;` | `aload/astore` |

---

## Соответствие конструкций Pascal → JVM-инструкции

### Переменные

Глобальные переменные (`var` в главном блоке) — **статические поля класса** (`putstatic`/`getstatic`).

Локальные переменные функций и параметры — **JVM local variable slots** (`iload`/`istore` и т.д.).

### Арифметика

| Pascal           | JVM            |
|-----------------|----------------|
| `a + b`         | `iadd` / `dadd` |
| `a - b`         | `isub` / `dsub` |
| `a * b`         | `imul` / `dmul` |
| `a / b`         | `idiv` / `ddiv` |
| `a div b`       | `idiv`          |
| `a mod b`       | `irem`          |

### Сравнения

Результат сравнения — `int` (0 или 1).

Целочисленные: `if_icmpeq`, `if_icmplt` и т.д.

Вещественные: `dcmpg` + `ifeq`/`ifne`/…

### Логические операции

`and` и `or` реализованы с **короткой схемой вычисления** (short-circuit evaluation).

`not` — `iconst_1` + `ixor`.

### Условный оператор (if)

```
; if cond then S1 else S2
<cond>
ifeq ELSE
<S1>
goto ENDIF
ELSE:
<S2>
ENDIF:
```

### Цикл while

```
WHILE_START:
  <cond>
  ifeq WHILE_END
  <body>
  goto WHILE_START
WHILE_END:
```

### Цикл for

```
<start> → istore slot_i
<end>   → istore slot_end
FOR_START:
  iload slot_i
  iload slot_end
  if_icmpgt FOR_END    ; (if_icmplt для downto)
  <body>
FOR_CONT:
  iload slot_i
  ldc 1
  iadd
  istore slot_i
  goto FOR_START
FOR_END:
```

### break / continue

`break` → `goto FOR_END / WHILE_END`

`continue` → `goto FOR_CONT / WHILE_START`

### Функции

Пользовательские функции компилируются в **статические методы** (`invokestatic`).

Параметры → первые слоты локальных переменных.

### writeln / write

```
getstatic java/lang/System/out Ljava/io/PrintStream;
<arg>
invokevirtual java/io/PrintStream/println(I)V
```

### read / readln

Чтение через `java.util.Scanner` (статическое поле `_scanner`):

```
getstatic ClassName/_scanner Ljava/util/Scanner;
invokevirtual java/util/Scanner/nextInt()I
istore slot
```

### Приведение типов (TypeConvert)

`integer → double`: `i2d`

`double → integer`: `d2i`

---

## Поддержка типа double

В рамках аттестации 3 в семантический анализатор добавлена полноценная поддержка типа `double`:

- `BaseType.DOUBLE` добавлен в перечисление типов
- `visit_Literal` определяет тип `float`-значений как `DOUBLE`
- `visit_BinOp` разрешает арифметику с `double`, автоматически вставляя `TypeConvertNode` при смешивании `integer` и `double`
- `visit_Cast` обрабатывает явные приведения `double(x)` и `integer(x)`
- `visit_UnOp` поддерживает унарный минус для `double`

---

## Запуск компилятора

```bash
# Только генерация .j файла
python main.py samples/fibonacci.pas

# Генерация + сборка + запуск (нужен jasmin.jar в корне проекта)
python main.py samples/fibonacci.pas --run

# Без вывода AST
python main.py samples/sqrt_binary.pas --no-ast

# Указать выходную папку
python main.py samples/minimal.pas --out build/
```

---

## Сборка и запуск вручную

```bash
# Генерировать .j файл
python main.py samples/fibonacci.pas

# Собрать .class с помощью Jasmin
java -jar jasmin.jar -d out/ out/Fibonacci.j

# Запустить
java -cp out/ Fibonacci
```

Скачать Jasmin: https://jasmin.sourceforge.net/

---

## Тестирование кодогенерации

```bash
# Сгенерировать .j для всех .pas файлов
python run_codegen_tests.py

# С обзором сгенерированного кода
python run_codegen_tests.py --verbose

# С компиляцией и запуском (нужен jasmin.jar)
python run_codegen_tests.py --run
```

---

## Пример сгенерированного кода

Для программы:

```pascal
program Demo;
var
  x: integer;
begin
  x := 2 + 3;
  writeln(x);
end.
```

Генерируется Jasmin:

```jasmin
.class public Demo
.super java/lang/Object

.field private static x I

.method public static main([Ljava/lang/String;)V
    .limit stack 16
    .limit locals 2
    iconst_0
    istore 1
    iconst_2
    iconst_3
    iadd
    istore 1
    getstatic java/lang/System/out Ljava/io/PrintStream;
    iload 1
    invokevirtual java/io/PrintStream/println(I)V
    return
.end method
```