import sys
import math

from Modelo import *

if __name__ == '__main__':
    c = ConfigParser.ConfigParser()
    c.read('IndustriaTextil.in')
    params = ParametrosSimulacao.fromConfig(c)

    a = int(float(sys.argv[1]))
    b = int(float(sys.argv[2]))
    pts = int(float(sys.argv[3]))

    custos = []
    capacidade = []
    for i in range(a, b, int(math.ceil((b-a)/pts))):
      params.armazenamento_capacidade = i
      saidas = Simulador(params).simular()

      custo_total = sum([saidas[k] for k in saidas.keys() if k.startswith('custo_')])
      custos.append(custo_total)
      capacidade.append(params.armazenamento_capacidade)

    print 'Y=%s;' % str(custos)
    print 'X=%s;' % str(capacidade)
    print 'plot(X, Y);'
