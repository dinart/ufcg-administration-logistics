Determinação dos Custos Logísticos de Estocagem a partir de Simulação Computacional
===================================================================================

Executando o Simulador
----------------------
Para executar o simulador, faça:

  python Modelo.py Entrada.in

O arquivo Entrada.in é um arquivo que contém as especificações da simulação.
Para simplificar, acompanha este código um exemplo de entrada chamado
ExemploEntradas.in.


Gerar Piechart dos Custos Logísticos
------------------------------------
Utilizar a função piechart.m feita para o octave. Para utilizá-la, basta estar
na mesma pasta, executar o octave e passar um vetor com os custos logísticos
(saída do simulador). Por exemplo:

 octave:1> piechart([333.33, 0.00, 0.04583, 52.8666, 386.346])


Gerar Gráficos Basicos
----------------------
Para gerar gráficos, basta usar a função 'plot', já presente no matlab/octave.
