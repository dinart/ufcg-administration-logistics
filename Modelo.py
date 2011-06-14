#!/usr/bin/python
# -*- coding: iso8859-1 -*-

# Copyright (c) 2011, André Dieb Martins <andre.dieb@gmail.com>
# Copyright (c) 2011, Dinart Duarte Braga <dinartd@gmail.com>
# Copyright (c) 2011, Felipe Gonçalves Assis <felipe.assis@ee.ufcg.edu.br>
# Copyright (c) 2011, Débora Diniz de Melo <debora.melo@ee.ufcg.edu.br>
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#   Redistributions of source code must retain the above copyright notice, this list
#   of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright notice, this
#   list of conditions and the following disclaimer in the documentation and/or other
#   materials provided with the distribution.
#
#   Neither the name of the Universidade Federal de Campina Grande nor the names of
#   its contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
# TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
import math
import random
import ConfigParser


class DistribuicaoWeibull(object):

    def __init__(self, l, k):
        """ Classe utilitária para lidar com a distribuição de Weibull.
        É definida por dois valores, l (formato) e escala 'k'.
        """
        self.l = l
        self.k = k

    def __call__(self):
        """ Gera um valor da distribuição.
        """
        return random.weibullvariate(self.k, self.l)

    def esperanca(self):
        """ Calcula o valor da esperança da distribuição de Weibull.
        """
        return self.l * math.gamma(1 + 1.0/self.k)


def media(vetor):
    """ Retorna o valor médio do vetor.
    """
    return sum(vetor)/len(vetor)

def desvio_padrao(vetor):
    """ Retorna o desvio padrão amostral do vetor.
    """
    m = media(vetor)
    return math.sqrt((1.0/(len(vetor) - 1)) * sum([math.pow(v - m, 2) for v in vetor]))


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
        self.gerador = DistribuicaoWeibull(params.weibull_k, params.weibull_l)
        self.falha_em = int(math.floor(self.gerador()))

    def recalcular_data_falha(self, dia_atual):
        while self.falha_em <= dia_atual:
            self.falha_em = dia_atual + int(math.floor(self.gerador()))

class Simulador(object):
    def __init__(self, params):
        self.params = params
        self.periodos = 100
        self.Ndias = int(self.periodos * DistribuicaoWeibull(params.weibull_l, params.weibull_k).esperanca())
        self.taxa_custo_oportunidade = math.pow(1 + params.custo_oportunidade_anual, 1.0/360.0) - 1
        self.equipamentos = [Equipamento(params) for i in range(int(self.params.items_operacao))]
        self.estoque = self.params.armazenamento_capacidade
        self.reposicoes = []
        self.saidas = {'estoque_evolucao': [],
                       'custo_transporte': 0.0,
                       'custo_estocagem': 0.0,
                       'custo_oportunidade': 0.0,
                       'custo_parada': 0.0}
        self.nfalhas = 0

    def normaliza(self, saidas):
        fator = 30/float(self.Ndias*(1 - 1/self.periodos))
        for k in saidas:
            if k.startswith('custo_'):
                saidas[k] *= fator

        saidas['estoque_evolucao'] = [int(k) for k in saidas['estoque_evolucao'][:]]
        return saidas

    def resetar(self):
        self.saidas = {'estoque_evolucao': [],
                       'custo_transporte': 0.0,
                       'custo_estocagem': 0.0,
                       'custo_oportunidade': 0.0,
                       'custo_parada': 0.0}

    def simular(self):
        for dia in range(self.Ndias):
            if dia == self.Ndias/self.periodos:
                self.resetar()
            self.processar_reposicoes()
            self.processar_falhas(dia)
            self.processar_estoque()
        return self.normaliza(self.saidas)

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
                self.nfalhas += 1

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
        self.saidas['custo_oportunidade'] = self.saidas['custo_oportunidade'] + (self.saidas['custo_oportunidade'] + self.estoque * self.params.item_preco) * self.taxa_custo_oportunidade

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

    print 'Simulação'
    for p, v in params.attrs.items():
      print '\t%s:\t%2.2f' % (p.replace('_', ' ').capitalize(), v)
    print '\tTempo de simulação:', (sim.Ndias - sim.Ndias/sim.periodos), 'dias'
    print
    print 'Estoque'
    print '\tCapacidade:', int(params.armazenamento_capacidade), 'itens'
    print '\tMenor número registrado de ítens estocados:', int(min(saidas['estoque_evolucao'])), 'itens'
    print '\tMédia:', media(saidas['estoque_evolucao']), 'itens'
    print '\tDesvio padrão:', desvio_padrao(saidas['estoque_evolucao'])
    print '\tEvolução:', saidas['estoque_evolucao'][:100] , 'itens/dia'
    print
    total = 0.0
    print 'Custos Mensais:'
    for custo in [k for k in saidas.keys() if k.startswith('custo')]:
        print '\t%s: %.3f R$/mês' % (custo.replace('_', ' ').capitalize(), saidas[custo])
        total += saidas[custo]

    print '\tTotal: %.3f R$/mês' % total

    print 'Relatório de Falhas'
    print '\tNumero de falhas:', sim.nfalhas, 'falhas'
    print '\tNumero de falhas:', sim.nfalhas/sim.Ndias, 'falhas/dia'
