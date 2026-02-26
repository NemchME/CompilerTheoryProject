program t;
var a, b: boolean;
begin
  a := true;
  b := false;
  if not a or a and b then
    a := false
  else
    a := true;
end.
