program Tree;
var
  i, j, spaces, stars: integer;
  n: integer;
begin
  n := 7;

  { Ёлочка }
  for i := 1 to n do
  begin
    spaces := n - i;
    stars  := 2 * i - 1;

    j := 1;
    while j <= spaces do
    begin
      write(' ');
      j := j + 1
    end;

    j := 1;
    while j <= stars do
    begin
      write('*');
      j := j + 1
    end;

    writeln()
  end;

  { Ствол }
  j := 1;
  while j <= 3 do
  begin
    i := 1;
    while i <= n - 1 do
    begin
      write(' ');
      i := i + 1
    end;
    writeln('|');
    j := j + 1
  end
end.