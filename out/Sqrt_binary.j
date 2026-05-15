.class public Sqrt_binary
.super java/lang/Object

.field static _scanner Ljava/util/Scanner;
.field static x D
.field static left D
.field static right D
.field static mid D
.field static i I

.method static <clinit>()V
    .limit stack 3
    .limit locals 0
    new java/util/Scanner
    dup
    getstatic java/lang/System/in Ljava/io/InputStream;
    invokespecial java/util/Scanner/<init>(Ljava/io/InputStream;)V
    putstatic Sqrt_binary/_scanner Ljava/util/Scanner;
    return
.end method

.method public static main([Ljava/lang/String;)V
    .limit stack 16
    .limit locals 26
    dconst_0
    dstore 1
    dconst_0
    dstore 3
    dconst_0
    dstore 5
    dconst_0
    dstore 7
    iconst_0
    istore 9
    ldc2_w 50.0
    dstore 1
    ldc2_w 0.0
    dstore 3
    dload 1
    dstore 5
    iconst_1
    istore 9
    sipush 200
    istore 10
FOR_START1:
    iload 9
    iload 10
    if_icmpgt FOR_END2
    dload 3
    dload 5
    dadd
    ldc2_w 2.0
    ddiv
    dstore 7
    dload 7
    dload 7
    dmul
    dload 1
    dcmpg
    ifgt CMP_TRUE4
    iconst_0
    goto CMP_END5
CMP_TRUE4:
    iconst_1
CMP_END5:
    ifeq ELSE6
    dload 7
    dstore 5
    goto ENDIF7
ELSE6:
    dload 7
    dstore 3
ENDIF7:
FOR_CONT3:
    iload 9
    ldc 1
    iadd
    istore 9
    goto FOR_START1
FOR_END2:
    getstatic java/lang/System/out Ljava/io/PrintStream;
    dload 7
    invokevirtual java/io/PrintStream/println(D)V
    return
.end method
