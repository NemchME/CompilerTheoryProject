program t;
var i, s: integer;
begin
  s := 0;
  for i := 1 to 5 do
    s := s + i;
  for i := 5 downto 1 do
  begin
    if i = 3 then continue;
    if i = 2 then break;
    s := s + i;
  end;
end.
