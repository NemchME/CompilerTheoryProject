.class public Mixed_operations
.super java/lang/Object

.field static _scanner Ljava/util/Scanner;
.field static a I
.field static b D
.field static c D

.method static <clinit>()V
    .limit stack 3
    .limit locals 0
    new java/util/Scanner
    dup
    getstatic java/lang/System/in Ljava/io/InputStream;
    invokespecial java/util/Scanner/<init>(Ljava/io/InputStream;)V
    putstatic Mixed_operations/_scanner Ljava/util/Scanner;
    return
.end method

.method public static main([Ljava/lang/String;)V
    .limit stack 16
    .limit locals 22
    iconst_0
    istore 1
    dconst_0
    dstore 2
    dconst_0
    dstore 4
    iconst_3
    istore 1
    ldc2_w 4.5
    dstore 2
    iload 1
    i2d
    dload 2
    dmul
    dload 2
    ldc2_w 2.0
    ddiv
    dadd
    ldc2_w 1.25
    dsub
    dstore 4
    return
.end method
