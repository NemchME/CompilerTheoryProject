.class public Precision_test
.super java/lang/Object

.field static _scanner Ljava/util/Scanner;
.field static x D
.field static y D
.field static i I

.method static <clinit>()V
    .limit stack 3
    .limit locals 0
    new java/util/Scanner
    dup
    getstatic java/lang/System/in Ljava/io/InputStream;
    invokespecial java/util/Scanner/<init>(Ljava/io/InputStream;)V
    putstatic Precision_test/_scanner Ljava/util/Scanner;
    return
.end method

.method public static main([Ljava/lang/String;)V
    .limit stack 16
    .limit locals 22
    dconst_0
    dstore 1
    dconst_0
    dstore 3
    iconst_0
    istore 5
    ldc2_w 1.0
    dstore 1
    iconst_1
    istore 5
    bipush 50
    istore 6
FOR_START1:
    iload 5
    iload 6
    if_icmpgt FOR_END2
    dload 1
    ldc2_w 2.0
    ddiv
    dstore 1
FOR_CONT3:
    iload 5
    ldc 1
    iadd
    istore 5
    goto FOR_START1
FOR_END2:
    dload 1
    ldc2_w 1024.0
    dmul
    dstore 3
    return
.end method
