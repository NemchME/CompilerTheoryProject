program Triangle;
var
  i, j, n: integer;
begin
  n := 8;

  for i := 1 to n do
  begin
    j := 1;
    while j <= i do
    begin
      write('#');
      write(' ');
      j := j + 1
    end;
    writeln()
  end;

  writeln();

  for i := 1 to n do
  begin
    j := 1;
    while j <= n - i do
    begin
      write(' ');
      j := j + 1
    end;
    j := 1;
    while j <= 2 * i - 1 do
    begin
      write('*');
      j := j + 1
    end;
    writeln()
  end
end.