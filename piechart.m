function piechart (data)
  pie(data)
  names = char("Transporte", "Interrupcao", "Oportunidade", "Estocagem")
  for i=1:4
    gtext(names(i, :));
  end
  title("Custos Logisticos", 'fontsize', 15)
endfunction
