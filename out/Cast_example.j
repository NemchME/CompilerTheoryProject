.class public Cast_example
.super java/lang/Object

.field static _scanner Ljava/util/Scanner;
.field static i I
.field static d D

.method static <clinit>()V
    .limit stack 3
    .limit locals 0
    new java/util/Scanner
    dup
    getstatic java/lang/System/in Ljava/io/InputStream;
    invokespecial java/util/Scanner/<init>(Ljava/io/InputStream;)V
    putstatic Cast_example/_scanner Ljava/util/Scanner;
    return
.end method

.method public static main([Ljava/lang/String;)V
    .limit stack 16
    .limit locals 20
    iconst_0
    istore 1
    dconst_0
    dstore 2
    bipush 7
    istore 1
    iload 1
    i2d
    ldc2_w 3.0
    ddiv
    dstore 2
    return
.end method
