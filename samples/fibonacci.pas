program Fibonacci;

var
  n, i: integer;
  a, b, temp: double;

begin
  n := 20;
  a := 0.0;
  b := 1.0;

  for i := 1 to n do
  begin
    temp := a + b;
    a := b;
    b := temp;
  end;
end.
