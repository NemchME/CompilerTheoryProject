.class public Math_demo
.super java/lang/Object

.field static _scanner Ljava/util/Scanner;
.field static x D
.field static y D
.field static z D
.field static i I

.method static <clinit>()V
    .limit stack 3
    .limit locals 0
    new java/util/Scanner
    dup
    getstatic java/lang/System/in Ljava/io/InputStream;
    invokespecial java/util/Scanner/<init>(Ljava/io/InputStream;)V
    putstatic Math_demo/_scanner Ljava/util/Scanner;
    return
.end method

.method public static main([Ljava/lang/String;)V
    .limit stack 16
    .limit locals 24
    dconst_0
    dstore 1
    dconst_0
    dstore 3
    dconst_0
    dstore 5
    iconst_0
    istore 7
    iconst_1
    istore 7
    bipush 10
    istore 8
FOR_START1:
    iload 7
    iload 8
    if_icmpgt FOR_END2
    iload 7
    i2d
    dstore 1
    dload 1
    invokestatic PascalRuntime/sqrt(D)D
    dstore 3
    dload 3
    invokestatic PascalRuntime/println(D)V
FOR_CONT3:
    iload 7
    ldc 1
    iadd
    istore 7
    goto FOR_START1
FOR_END2:
    invokestatic PascalRuntime/println()V
    iconst_3
    iconst_3
    imul
    iconst_4
    iconst_4
    imul
    iadd
    i2d
    invokestatic PascalRuntime/sqrt(D)D
    dstore 1
    dload 1
    invokestatic PascalRuntime/println(D)V
    invokestatic PascalRuntime/println()V
    iconst_0
    istore 7
    bipush 6
    istore 9
FOR_START4:
    iload 7
    iload 9
    if_icmpgt FOR_END5
    iload 7
    i2d
    ldc2_w 0.5
    dmul
    dstore 1
    dload 1
    invokestatic PascalRuntime/sin(D)D
    dstore 3
    dload 1
    invokestatic PascalRuntime/cos(D)D
    dstore 5
    dload 3
    invokestatic PascalRuntime/print(D)V
    ldc " "
    invokestatic PascalRuntime/print(Ljava/lang/String;)V
    dload 5
    invokestatic PascalRuntime/println(D)V
FOR_CONT6:
    iload 7
    ldc 1
    iadd
    istore 7
    goto FOR_START4
FOR_END5:
    return
.end method
