public class PascalRuntime {

    private static final double PI = 3.14159265358979323846;
    private static final double E  = 2.71828182845904523536;

    private static final java.io.FileOutputStream stdout;
    static {
        stdout = new java.io.FileOutputStream(java.io.FileDescriptor.out);
    }

    private static void writeBytes(byte[] bytes) {
        try {
            stdout.write(bytes);
        } catch (java.io.IOException e) {
        }
    }

    public static void print(String s) {
        writeBytes(s.getBytes());
    }

    public static void println(String s) {
        writeBytes((s + "\n").getBytes());
    }

    public static void print(int x) {
        writeBytes(intToString(x).getBytes());
    }

    public static void println(int x) {
        writeBytes((intToString(x) + "\n").getBytes());
    }

    public static void print(double x) {
        writeBytes(doubleToString(x).getBytes());
    }

    public static void println(double x) {
        writeBytes((doubleToString(x) + "\n").getBytes());
    }

    public static void println() {
        writeBytes("\n".getBytes());
    }

    private static String intToString(int x) {
        if (x == 0) return "0";
        boolean negative = x < 0;
        if (negative) x = -x;
        char[] buf = new char[12];
        int pos = 11;
        while (x > 0) {
            buf[pos--] = (char)('0' + x % 10);
            x /= 10;
        }
        if (negative) buf[pos--] = '-';
        return new String(buf, pos + 1, 11 - pos);
    }

    private static String doubleToString(double x) {
        if (x != x) return "NaN";
        if (x == Double.POSITIVE_INFINITY) return "Infinity";
        if (x == Double.NEGATIVE_INFINITY) return "-Infinity";
        if (x == 0.0) return "0.0";

        StringBuilder sb = new StringBuilder();
        if (x < 0) { sb.append('-'); x = -x; }

        long intPart = (long) x;
        double fracPart = x - intPart;
        sb.append(intToString((int) intPart));
        sb.append('.');

        for (int i = 0; i < 15; i++) {
            fracPart *= 10;
            int digit = (int) fracPart;
            sb.append((char)('0' + digit));
            fracPart -= digit;
        }

        String s = sb.toString();
        int end = s.length();
        while (end > s.indexOf('.') + 2 && s.charAt(end - 1) == '0') end--;
        return s.substring(0, end);
    }

    public static double sqrt(double x) {
        if (x < 0) return Double.NaN;
        if (x == 0) return 0;
        double guess = x / 2.0;
        for (int i = 0; i < 60; i++) {
            guess = (guess + x / guess) / 2.0;
        }
        return guess;
    }

    public static double sin(double x) {
        x = x % (2 * PI);
        double result = 0;
        double term   = x;
        for (int n = 1; n <= 20; n++) {
            result += term;
            term *= -x * x / ((2 * n) * (2 * n + 1));
        }
        return result;
    }

    public static double cos(double x) {
        x = x % (2 * PI);
        double result = 0;
        double term   = 1.0;
        for (int n = 1; n <= 20; n++) {
            result += term;
            term *= -x * x / ((2 * n - 1) * (2 * n));
        }
        return result;
    }

    public static double tan(double x) {
        double c = cos(x);
        if (c == 0) return Double.NaN;
        return sin(x) / c;
    }

    public static double exp(double x) {
        double result = 1.0;
        double term   = 1.0;
        for (int n = 1; n <= 30; n++) {
            term *= x / n;
            result += term;
        }
        return result;
    }

    public static double ln(double x) {
        if (x <= 0) return Double.NaN;
        double y = x - 1;
        for (int i = 0; i < 100; i++) {
            double ey = exp(y);
            y = y - (ey - x) / ey;
        }
        return y;
    }

    public static double abs_double(double x) { return x < 0 ? -x : x; }
    public static int    abs(int x)           { return x < 0 ? -x : x; }
    public static int    sqr(int x)           { return x * x; }

    public static double floor(double x) {
        long l = (long) x;
        return (x < 0 && x != l) ? l - 1 : l;
    }

    public static double ceil(double x) {
        long l = (long) x;
        return (x > 0 && x != l) ? l + 1 : l;
    }

    public static double frac(double x)  { return x - floor(x); }
    public static int    round(double x) { return (int) floor(x + 0.5); }
    public static int    trunc(double x) { return (int) x; }

    public static double arcsin(double x) {
        if (x < -1 || x > 1) return Double.NaN;
        if (x == 1)  return PI / 2;
        if (x == -1) return -PI / 2;
        return arctan(x / sqrt(1.0 - x * x));
    }

    public static double arccos(double x) {
        if (x < -1 || x > 1) return Double.NaN;
        return PI / 2 - arcsin(x);
    }

    public static double arctan(double x) {
        if (x > 1)  return PI / 2 - arctan(1.0 / x);
        if (x < -1) return -PI / 2 - arctan(1.0 / x);
        double result = 0;
        double term   = x;
        double x2     = x * x;
        for (int n = 0; n < 50; n++) {
            result += term / (2 * n + 1);
            term *= -x2;
        }
        return result;
    }
}