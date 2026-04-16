program Demo;
var
  x: integer;

function f(a: integer): integer;
var x: double;
begin
  x :=  a + 1;
  return x;
end;

begin
  x := f(5);
  writeln(x)
end.