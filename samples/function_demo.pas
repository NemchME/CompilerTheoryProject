program Demo;
var
  x: integer;

function f(a: integer): integer;
begin
  return a + 1;
end;

begin
  x := f(5);
  writeln(x)
end.
