# CompilerTheoryProject

### Объявления

* секция `var`
* типы: `integer`, `char`, `boolean`

### Операторы

* присваивание `:=`
* условный оператор `if ... then ... else`
* цикл `while ... do`
* цикл `for ... to/downto ... do`
* `break`
* `continue`
* ввод/вывод:

  * `read`, `readln`
  * `write`, `writeln`

### Выражения

* арифметические операции: `+ - * / div mod`
* операции сравнения: `= <> < <= > >=`
* логические операции: `not`, `and`, `or`
* литералы: целые, символьные, булевы
* скобки

Приоритет операций:

```
not > and > or
```

## Структура проекта

```
src/
  pascal/
    lexer.py
    parser.py
  ast/
    nodes.py
samples/
  tests/
run_tests.py
```

## Запуск тестов

```bash
python run_tests.py
```