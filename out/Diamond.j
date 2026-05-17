.class public Diamond
.super java/lang/Object

.field static _scanner Ljava/util/Scanner;
.field static i I
.field static j I
.field static n I
.field static spaces I
.field static stars I

.method static <clinit>()V
    .limit stack 3
    .limit locals 0
    new java/util/Scanner
    dup
    getstatic java/lang/System/in Ljava/io/InputStream;
    invokespecial java/util/Scanner/<init>(Ljava/io/InputStream;)V
    putstatic Diamond/_scanner Ljava/util/Scanner;
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
    iconst_5
    istore 3
    iconst_1
    istore 1
    iload 3
    istore 6
FOR_START1:
    iload 1
    iload 6
    if_icmpgt FOR_END2
    iload 3
    iload 1
    isub
    istore 4
    iconst_2
    iload 1
    imul
    iconst_1
    isub
    istore 5
    iconst_1
    istore 2
WHILE_START4:
    iload 2
    iload 4
    if_icmple CMP_TRUE6
    iconst_0
    goto CMP_END7
CMP_TRUE6:
    iconst_1
CMP_END7:
    ifeq WHILE_END5
    getstatic java/lang/System/out Ljava/io/PrintStream;
    ldc " "
    invokevirtual java/io/PrintStream/print(Ljava/lang/String;)V
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
    iload 5
    if_icmple CMP_TRUE10
    iconst_0
    goto CMP_END11
CMP_TRUE10:
    iconst_1
CMP_END11:
    ifeq WHILE_END9
    getstatic java/lang/System/out Ljava/io/PrintStream;
    ldc "*"
    invokevirtual java/io/PrintStream/print(Ljava/lang/String;)V
    iload 2
    iconst_1
    iadd
    istore 2
    goto WHILE_START8
WHILE_END9:
    getstatic java/lang/System/out Ljava/io/PrintStream;
    invokevirtual java/io/PrintStream/println()V
FOR_CONT3:
    iload 1
    ldc 1
    iadd
    istore 1
    goto FOR_START1
FOR_END2:
    iload 3
    iconst_1
    isub
    istore 1
    iconst_1
    istore 7
FOR_START12:
    iload 1
    iload 7
    if_icmplt FOR_END13
    iload 3
    iload 1
    isub
    istore 4
    iconst_2
    iload 1
    imul
    iconst_1
    isub
    istore 5
    iconst_1
    istore 2
WHILE_START15:
    iload 2
    iload 4
    if_icmple CMP_TRUE17
    iconst_0
    goto CMP_END18
CMP_TRUE17:
    iconst_1
CMP_END18:
    ifeq WHILE_END16
    getstatic java/lang/System/out Ljava/io/PrintStream;
    ldc " "
    invokevirtual java/io/PrintStream/print(Ljava/lang/String;)V
    iload 2
    iconst_1
    iadd
    istore 2
    goto WHILE_START15
WHILE_END16:
    iconst_1
    istore 2
WHILE_START19:
    iload 2
    iload 5
    if_icmple CMP_TRUE21
    iconst_0
    goto CMP_END22
CMP_TRUE21:
    iconst_1
CMP_END22:
    ifeq WHILE_END20
    getstatic java/lang/System/out Ljava/io/PrintStream;
    ldc "*"
    invokevirtual java/io/PrintStream/print(Ljava/lang/String;)V
    iload 2
    iconst_1
    iadd
    istore 2
    goto WHILE_START19
WHILE_END20:
    getstatic java/lang/System/out Ljava/io/PrintStream;
    invokevirtual java/io/PrintStream/println()V
FOR_CONT14:
    iload 1
    ldc -1
    iadd
    istore 1
    goto FOR_START12
FOR_END13:
    return
.end method
