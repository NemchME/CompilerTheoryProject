program Test;
var
  x: integer;
begin
  x := 5;
  if x > 2 then
    x := x - 1;

  while x > 0 do
    x := x - 1;
end.