.class public Tree
.super java/lang/Object

.field static _scanner Ljava/util/Scanner;
.field static i I
.field static j I
.field static spaces I
.field static stars I
.field static n I

.method static <clinit>()V
    .limit stack 3
    .limit locals 0
    new java/util/Scanner
    dup
    getstatic java/lang/System/in Ljava/io/InputStream;
    invokespecial java/util/Scanner/<init>(Ljava/io/InputStream;)V
    putstatic Tree/_scanner Ljava/util/Scanner;
    return
.end method

.method public static main([Ljava/lang/String;)V
    .limit stack 16
    .limit locals 22
    iconst_0
    istore 1
    iconst_0
    istore 2
    iconst_0
    istore 3
    iconst_0
    istore 4
    iconst_0
    istore 5
    bipush 7
    istore 5
    iconst_1
    istore 1
    iload 5
    istore 6
FOR_START1:
    iload 1
    iload 6
    if_icmpgt FOR_END2
    iload 5
    iload 1
    isub
    istore 3
    iconst_2
    iload 1
    imul
    iconst_1
    isub
    istore 4
    iconst_1
    istore 2
WHILE_START4:
    iload 2
    iload 3
    if_icmple CMP_TRUE6
    iconst_0
    goto CMP_END7
CMP_TRUE6:
    iconst_1
CMP_END7:
    ifeq WHILE_END5
    ldc " "
    invokestatic PascalRuntime/print(Ljava/lang/String;)V
    iload 2
    iconst_1
    iadd
    istore 2
    goto WHILE_START4
WHILE_END5:
    iconst_1
    istore 2
WHILE_START8:
    iload 2
    iload 4
    if_icmple CMP_TRUE10
    iconst_0
    goto CMP_END11
CMP_TRUE10:
    iconst_1
CMP_END11:
    ifeq WHILE_END9
    ldc "*"
    invokestatic PascalRuntime/print(Ljava/lang/String;)V
    iload 2
    iconst_1
    iadd
    istore 2
    goto WHILE_START8
WHILE_END9:
    invokestatic PascalRuntime/println()V
FOR_CONT3:
    iload 1
    ldc 1
    iadd
    istore 1
    goto FOR_START1
FOR_END2:
    iconst_1
    istore 2
WHILE_START12:
    iload 2
    iconst_3
    if_icmple CMP_TRUE14
    iconst_0
    goto CMP_END15
CMP_TRUE14:
    iconst_1
CMP_END15:
    ifeq WHILE_END13
    iconst_1
    istore 1
WHILE_START16:
    iload 1
    iload 5
    iconst_1
    isub
    if_icmple CMP_TRUE18
    iconst_0
    goto CMP_END19
CMP_TRUE18:
    iconst_1
CMP_END19:
    ifeq WHILE_END17
    ldc " "
    invokestatic PascalRuntime/print(Ljava/lang/String;)V
    iload 1
    iconst_1
    iadd
    istore 1
    goto WHILE_START16
WHILE_END17:
    ldc "|"
    invokestatic PascalRuntime/println(Ljava/lang/String;)V
    iload 2
    iconst_1
    iadd
    istore 2
    goto WHILE_START12
WHILE_END13:
    return
.end method
