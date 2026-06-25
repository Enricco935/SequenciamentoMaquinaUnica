from data_base import *
class Chapa:
    def __init__(self, id, tipo, tempo_processamento):
        self.id = id
        self.tipo = tipo
        self.tempo_processamento = tempo_processamento
class Pedido:
    def __init__(self, id, chapas, tempo_processamento, data_termino, custo_antecipacao, custo_atraso):
        self.id = id
        self.chapas = chapas # chapas do pedido
        self.tempo_processamento = tempo_processamento 
        self.data_termino = data_termino
        self.custo_antecipacao = custo_antecipacao
        self.custo_atraso = custo_atraso
class Job: 
    # informacoes necessarias para cada job
    def __init__(self, id_chapa ,tempo_processamento, data_termino, custo_antecipacao, custo_atraso):
        self.id_chapa = id_chapa
        self.tempo_processamento = tempo_processamento
        self.data_termino = data_termino
        self.custo_antecipacao = custo_antecipacao
        self.custo_atraso = custo_atraso
class Entrada_Modelo:
    def __init__(self, n, P, D, S, a, b):
        self.n = n #numero de jobs
        self.P = P #vetor tempo processamento dos jobs
        self.D = D #vetor data desejada para o termino
        self.S = S #dict Setup
        self.a = a #tupla custo antecipacao dos jobs
        self.b = b #tupla custo atraso dos jobs
        self.M = 99999
class Variaveis_decisao:
    def __init__(self, s, y, e, t, Z):
        self.s = s #tupla tempo inicio do processamento
        self.y = y #matriz antecedencia
        self.e = e #tupla tempo antecipacao
        self.t = t #tupla tempo de atraso
        self.Z = Z #custo


def dicionario_setup(dados_setup):
    setups = {}
    for origem, destino, tempo in dados_setup:
        setups[(origem, destino)] = tempo
    return setups



def chapas_por_pedido(pedido_id):
    chapas = []
    dados_chapas_pedido = listar_chapas_por_pedido(pedido_id)
    for id, tipo, tempo_processamento_chapa, quantidade in dados_chapas_pedido:
        chapas.append(Chapa(id, tipo, tempo_processamento_chapa * quantidade))

    return chapas

def dados_entrada_modelo(jobs, dados_setup):
    n_jobs = len(jobs)

    vetor_tempo_processamento = []
    vetor_data_termino = []
    vetor_custo_antecipacao = []
    vetor_custo_atraso = []
    matriz_setup = []
    setups = dicionario_setup(dados_setup)

    for i ,job in enumerate(jobs):
        matriz_setup.append([])
        for job2 in jobs:
            matriz_setup[i].append(setups[(job.id_chapa,job2.id_chapa)])
        vetor_tempo_processamento.append(job.tempo_processamento)
        vetor_data_termino.append(job.data_termino)
        vetor_custo_antecipacao.append(job.custo_antecipacao)
        vetor_custo_atraso.append(job.custo_atraso)

    return Entrada_Modelo(n_jobs, vetor_tempo_processamento, vetor_data_termino, matriz_setup, vetor_custo_antecipacao, vetor_custo_atraso)
    

dados_chapas = listar_chapas()
dados_setups = listar_setups()
dados_pedido = listar_pedidos()

chapas = []
pedidos = []
jobs = []
setups = dicionario_setup(dados_setups)
entrada = None

#===== preenche chapas
for i, (id_chapa, tipo, tempo_processamento) in enumerate(dados_chapas):
    chapas.append(Chapa(id_chapa, tipo, tempo_processamento))

for id, data_termino, custo_antecipacao, custo_atraso, tempo_processamento, chapas_distintas, qtd_chapas in dados_pedido:
    pedidos.append(Pedido(id, chapas_por_pedido(id), tempo_processamento, data_termino, custo_antecipacao, custo_atraso))

#tempo de setup entre uma chapa e outra e representado por dicionario
for pedido in pedidos:
    for chapa in pedido.chapas:
        jobs.append(Job(chapa.id_chapa,chapa.tempo_processamento, pedido.data_termino, pedido.custo_antecipacao, pedido.custo_atraso))

entrada = dados_entrada_modelo(jobs, dados_setups)
