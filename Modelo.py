#!/usr/bin/python
# -*- coding: iso8859-1 -*-

import sys
import random
import ConfigParser


def geradorDistribuicaoWeibull(k, l):
    def gerador():
        return random.weibullvariate(k, l)
    return gerador

class ParametrosSimulacao:

    @classmethod
    def fromConfig(cls, c):
        instance = cls()
        instance.attrs = []
        for k, v in c.items('Entradas'):
            setattr(instance, k, v)
            instance.attrs.append(k)
        return instance

    def __str__(self):
        return '<ParametrosSimulacao %s>' % \
            (' '.join('%s=%s' % (k, getattr(self, k)) for k in self.attrs))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Erro: modo de execução não identificado.'
        print 'Uso: %s <Parametros de Entrada.in>' % sys.argv[0]
        sys.exit(-1)

    c = ConfigParser.ConfigParser()
    c.read([sys.argv[1]])
    params = ParametrosSimulacao.fromConfig(c)
    print params
