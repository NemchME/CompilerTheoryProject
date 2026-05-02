program Precision;

var
  x, y: double;
  i: integer;

begin
  x := 1.0;
  for i := 1 to 50 do
    x := x / 2.0;

  y := x * 1024.0;
end.
