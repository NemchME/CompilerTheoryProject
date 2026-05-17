program MathDemo;
var
  x, y, z: double;
  i: integer;
begin
  for i := 1 to 10 do
  begin
    x := double(i);
    y := sqrt(x);
    writeln(y)
  end;

  writeln();

  x := sqrt(double(3 * 3 + 4 * 4));
  writeln(x);

  writeln();

  for i := 0 to 6 do
  begin
    x := double(i) * 0.5;
    y := sin(x);
    z := cos(x);
    write(y);
    write(' ');
    writeln(z)
  end
end.