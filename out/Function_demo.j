.class public Function_demo
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
    putstatic Function_demo/_scanner Ljava/util/Scanner;
    return
.end method

.method public static f(I)I
    .limit stack 16
    .limit locals 19
    dconst_0
    dstore 1
    iload 0
    iconst_1
    iadd
    i2d
    dstore 1
    dload 1
    d2i
    ireturn
    iconst_0
    ireturn
.end method

.method public static main([Ljava/lang/String;)V
    .limit stack 16
    .limit locals 18
    iconst_0
    istore 1
    iconst_5
    invokestatic Function_demo/f(I)I
    istore 1
    getstatic java/lang/System/out Ljava/io/PrintStream;
    iload 1
    invokevirtual java/io/PrintStream/println(I)V
    return
.end method
