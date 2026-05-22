.class public Minimal
.super java/lang/Object

.field static _scanner Ljava/util/Scanner;
.field static x I

.method static <clinit>()V
    .limit stack 3
    .limit locals 0
    new java/util/Scanner
    dup
    getstatic java/lang/System/in Ljava/io/InputStream;
    invokespecial java/util/Scanner/<init>(Ljava/io/InputStream;)V
    putstatic Minimal/_scanner Ljava/util/Scanner;
    return
.end method

.method public static main([Ljava/lang/String;)V
    .limit stack 16
    .limit locals 18
    iconst_0
    istore 1
    iconst_2
    iconst_3
    iconst_4
    imul
    iadd
    istore 1
    iload 1
    bipush 10
    if_icmpgt CMP_TRUE1
    iconst_0
    goto CMP_END2
CMP_TRUE1:
    iconst_1
CMP_END2:
    ifeq ENDIF3
    iload 1
    iconst_1
    isub
    istore 1
ENDIF3:
WHILE_START4:
    iload 1
    iconst_0
    if_icmpgt CMP_TRUE6
    iconst_0
    goto CMP_END7
CMP_TRUE6:
    iconst_1
CMP_END7:
    ifeq WHILE_END5
    iload 1
    iconst_1
    isub
    istore 1
    goto WHILE_START4
WHILE_END5:
    iload 1
    invokestatic PascalRuntime/println(I)V
    return
.end method
