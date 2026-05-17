program Diamond;
var
  i, j, n, spaces, stars: integer;
begin
  n := 5;

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

  for i := n - 1 downto 1 do
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
  end
end.