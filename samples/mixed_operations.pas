program MixedOps;

var
  a: integer;
  b, c: double;

begin
  a := 3;
  b := 4.5;
  c := double(a) * b + (b / 2.0) - 1.25;
end.
