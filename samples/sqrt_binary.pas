program SqrtBinary;

var
  x, left, right, mid: double;
  i: integer;

begin
  x := 50.0;
  left := 0.0;
  right := x;

  for i := 1 to 200 do
  begin
    mid := (left + right) / 2.0;
    if mid * mid > x then
      right := mid
    else
      left := mid;
  end;
end.
