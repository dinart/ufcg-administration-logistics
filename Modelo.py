#!/usr/bin/python
# -*- coding: iso8859-1 -*-

import sys
import math
import random
import ConfigParser


def geradorDistribuicaoWeibull(l, k):
    def gerador():
        return random.weibullvariate(k, l)
    return gerador

def media(vetor):
    return sum(vetor)/len(vetor)


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
        self.taxa_custo_oportunidade = math.pow(1 + params.custo_oportunidade_anual, 1.0/360.0) - 1
        self.gerador = geradorDistribuicaoWeibull(params.weibull_k, params.weibull_l)
        self.instantes_de_falhas = [int(math.floor(self.gerador())) for i in range(int(params.n_maquinas))]
        self.estoque = self.params.armazenamento_capacidade
        self.reposicoes = []
        self.saidas = {'estoque_evolucao': [],
                       'custo_transporte': 0.0,
                       'custo_estocagem': 0.0,
                       'custo_oportunidade': 0.0}

    def simular(self):
        for dia in range(360):
            self.processar_reposicoes()
            self.processar_falhas(dia)
            self.processar_estoque()
        return self.saidas

    def processar_reposicoes(self):
        espelho = []
        for i in range(len(self.reposicoes)):
            if self.reposicoes[i][0] == 1:
                self.estoque += self.reposicoes[i][1]
                self.saidas['custo_transporte'] += \
                    (self.params.transporte_custo_base + \
                     self.params.transporte_custo_unidade_extra * self.reposicoes[i][1])
            else:
                espelho.append([self.reposicoes[i][0] - 1, self.reposicoes[i][1]])
        self.reposicoes = espelho

    def processar_falhas(self, dia):
        if dia in self.instantes_de_falhas:
            # Indice da maquina falha
            indice = self.instantes_de_falhas.index(dia)
            # Calcular nova data de falha
            self.instantes_de_falhas[indice] = int(math.floor(self.gerador()))

    def processar_estoque(self):
        delta = self.estoque - self.params.armazenamento_capacidade
        if delta < 0:
            # Abaixo do máximo
            pedido = abs(delta)

            # Pedir apenas se alcançarmos o pedido mínimo
            if pedido >= self.params.pedido_minimo:
                self.efetuar_pedido(pedido)
        self.saidas['estoque_evolucao'].append(self.estoque)
        self.saidas['custo_estocagem'] += self.estoque * self.params.armazenamento_custo_unitario
        self.saidas['custo_oportunidade'] = (self.saidas['custo_oportunidade'] + self.estoque * self.params.item_preco) * self.taxa_custo_oportunidade

    def efetuar_pedido(self, quantidade):
        self.reposicoes.append([self.params.tempo_de_entrega_reposicao, quantidade])

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
