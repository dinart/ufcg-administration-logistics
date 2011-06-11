#!/usr/bin/python
# -*- coding: iso8859-1 -*-

import sys
import random
import ConfigParser


def geradorDistribuicaoWeibull(l, k):
    def gerador():
        return random.weibullvariate(k, l)
    return gerador


class ParametrosSimulacao(object):

    @classmethod
    def fromConfig(cls, c):
        instance = cls()
        instance.attrs = {}
        for k, v in c.items('Entradas'):
            instance.attrs[k] = float(v)
        return instance

    def __str__(self):
        return '<ParametrosSimulacao %s>' % \
            (' '.join('%s=%s' % (k, getattr(self, k)) for k in self.attrs))

    def __getattr__(self, k):
        return self.attrs.get(k, None)


class Simulador(object):
    def __init__(self, params):
        self.params = params
        self.gerador = geradorDistribuicaoWeibull(params.weibull_k, params.weibull_l)
        self.instantes_de_falhas = [self.gerador() for i in range(int(params.n_maquinas))]
        print 'Falhas:', self.instantes_de_falhas
        self.estoque = 0

    def simular(self):
        for dia in range(360):
            pass
        return []

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Erro: modo de execução não identificado.'
        print 'Uso: %s <Parametros de Entrada.in>' % sys.argv[0]
        sys.exit(-1)

    c = ConfigParser.ConfigParser()
    c.read([sys.argv[1]])
    params = ParametrosSimulacao.fromConfig(c)
    sim = Simulador(params)
    saidas = sim.simular()
    print saidas
