.class public Triangle
.super java/lang/Object

.field static _scanner Ljava/util/Scanner;
.field static i I
.field static j I
.field static n I

.method static <clinit>()V
    .limit stack 3
    .limit locals 0
    new java/util/Scanner
    dup
    getstatic java/lang/System/in Ljava/io/InputStream;
    invokespecial java/util/Scanner/<init>(Ljava/io/InputStream;)V
    putstatic Triangle/_scanner Ljava/util/Scanner;
    return
.end method

.method public static main([Ljava/lang/String;)V
    .limit stack 16
    .limit locals 20
    iconst_0
    istore 1
    iconst_0
    istore 2
    iconst_0
    istore 3
    bipush 8
    istore 3
    iconst_1
    istore 1
    iload 3
    istore 4
FOR_START1:
    iload 1
    iload 4
    if_icmpgt FOR_END2
    iconst_1
    istore 2
WHILE_START4:
    iload 2
    iload 1
    if_icmple CMP_TRUE6
    iconst_0
    goto CMP_END7
CMP_TRUE6:
    iconst_1
CMP_END7:
    ifeq WHILE_END5
    ldc "#"
    invokestatic PascalRuntime/print(Ljava/lang/String;)V
    ldc " "
    invokestatic PascalRuntime/print(Ljava/lang/String;)V
    iload 2
    iconst_1
    iadd
    istore 2
    goto WHILE_START4
WHILE_END5:
    invokestatic PascalRuntime/println()V
FOR_CONT3:
    iload 1
    ldc 1
    iadd
    istore 1
    goto FOR_START1
FOR_END2:
    invokestatic PascalRuntime/println()V
    iconst_1
    istore 1
    iload 3
    istore 5
FOR_START8:
    iload 1
    iload 5
    if_icmpgt FOR_END9
    iconst_1
    istore 2
WHILE_START11:
    iload 2
    iload 3
    iload 1
    isub
    if_icmple CMP_TRUE13
    iconst_0
    goto CMP_END14
CMP_TRUE13:
    iconst_1
CMP_END14:
    ifeq WHILE_END12
    ldc " "
    invokestatic PascalRuntime/print(Ljava/lang/String;)V
    iload 2
    iconst_1
    iadd
    istore 2
    goto WHILE_START11
WHILE_END12:
    iconst_1
    istore 2
WHILE_START15:
    iload 2
    iconst_2
    iload 1
    imul
    iconst_1
    isub
    if_icmple CMP_TRUE17
    iconst_0
    goto CMP_END18
CMP_TRUE17:
    iconst_1
CMP_END18:
    ifeq WHILE_END16
    ldc "*"
    invokestatic PascalRuntime/print(Ljava/lang/String;)V
    iload 2
    iconst_1
    iadd
    istore 2
    goto WHILE_START15
WHILE_END16:
    invokestatic PascalRuntime/println()V
FOR_CONT10:
    iload 1
    ldc 1
    iadd
    istore 1
    goto FOR_START8
FOR_END9:
    return
.end method
