.class public Fibonacci
.super java/lang/Object

.field static _scanner Ljava/util/Scanner;
.field static n I
.field static i I
.field static a D
.field static b D
.field static temp D

.method static <clinit>()V
    .limit stack 3
    .limit locals 0
    new java/util/Scanner
    dup
    getstatic java/lang/System/in Ljava/io/InputStream;
    invokespecial java/util/Scanner/<init>(Ljava/io/InputStream;)V
    putstatic Fibonacci/_scanner Ljava/util/Scanner;
    return
.end method

.method public static main([Ljava/lang/String;)V
    .limit stack 16
    .limit locals 25
    iconst_0
    istore 1
    iconst_0
    istore 2
    dconst_0
    dstore 3
    dconst_0
    dstore 5
    dconst_0
    dstore 7
    bipush 20
    istore 1
    ldc2_w 0.0
    dstore 3
    ldc2_w 1.0
    dstore 5
    iconst_1
    istore 2
    iload 1
    istore 9
FOR_START1:
    iload 2
    iload 9
    if_icmpgt FOR_END2
    dload 3
    dload 5
    dadd
    dstore 7
    dload 5
    dstore 3
    dload 7
    dstore 5
FOR_CONT3:
    iload 2
    ldc 1
    iadd
    istore 2
    goto FOR_START1
FOR_END2:
    getstatic java/lang/System/out Ljava/io/PrintStream;
    dload 5
    invokevirtual java/io/PrintStream/println(D)V
    return
.end method
