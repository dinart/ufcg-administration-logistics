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


class Equipamento(object):
    def __init__(self, params):
        # Gerar automaticamente
        self.operando = True
        self.gerador = geradorDistribuicaoWeibull(params.weibull_k, params.weibull_l)
        self.falha_em = int(math.floor(self.gerador()))

    def recalcular_data_falha(self, dia_atual):
        self.falha_em = dia_atual + int(math.floor(self.gerador()))

class Simulador(object):
    def __init__(self, params):
        self.params = params
        self.taxa_custo_oportunidade = math.pow(1 + params.custo_oportunidade_anual, 1.0/360.0) - 1
        self.equipamentos = [Equipamento(params) for i in range(int(self.params.items_operacao))]
        self.estoque = self.params.armazenamento_capacidade
        self.reposicoes = []
        self.saidas = {'estoque_evolucao': [],
                       'custo_transporte': 0.0,
                       'custo_estocagem': 0.0,
                       'custo_oportunidade': 0.0,
                       'custo_parada': 0.0}

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
        for eq in self.equipamentos:
            if not eq.operando:
                if self.estoque > 0:
                    # Voltar a operar
                    self.estoque -= 1
                    eq.operando = True
                    eq.recalcular_data_falha(dia)
                else:
                    self.saidas['custo_parada'] += self.params.custo_interrupcao_diario

            if eq.falha_em == dia:
                if self.estoque > 0:
                    # Substituir do estoque
                    self.estoque -= 1

                    # Calcular nova data de falha
                    eq.recalcular_data_falha(dia)
                else:
                    # Nao há para reposição, mantém no vetor
                    eq.operando = False
                    self.saidas['custo_parada'] += self.params.custo_interrupcao_diario

    def processar_estoque(self):
        delta = self.estoque - self.params.armazenamento_capacidade
        if delta < 0:
            # Abaixo do máximo
            pedido = abs(delta)

            # Calcular quanto já está por vir
            total = 0
            for p in self.reposicoes:
                total += p[1]

            # Pedir apenas se alcançarmos o pedido mínimo e já não há pedidos
            if self.estoque + total < self.params.armazenamento_capacidade and \
                pedido >= self.params.pedido_minimo:
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
    print 'Simulação: ' + str(params)
    saidas = sim.simular()
    print saidas
