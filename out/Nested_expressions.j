.class public Nested_expressions
.super java/lang/Object

.field static _scanner Ljava/util/Scanner;
.field static x D
.field static y D

.method static <clinit>()V
    .limit stack 3
    .limit locals 0
    new java/util/Scanner
    dup
    getstatic java/lang/System/in Ljava/io/InputStream;
    invokespecial java/util/Scanner/<init>(Ljava/io/InputStream;)V
    putstatic Nested_expressions/_scanner Ljava/util/Scanner;
    return
.end method

.method public static main([Ljava/lang/String;)V
    .limit stack 16
    .limit locals 21
    dconst_0
    dstore 1
    dconst_0
    dstore 3
    ldc2_w 10.0
    dstore 1
    dload 1
    ldc2_w 2.0
    dadd
    dload 1
    ldc2_w 3.0
    dsub
    dmul
    ldc2_w 2.0
    dload 1
    ldc2_w 5.0
    ddiv
    dadd
    ddiv
    dstore 3
    return
.end method
