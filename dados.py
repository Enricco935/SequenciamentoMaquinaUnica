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
    def __init__(self, nome_chapa, id_chapa ,tempo_processamento, data_termino, custo_antecipacao, custo_atraso):
        self.nome_chapa = nome_chapa
        self.id_chapa = id_chapa
        self.tempo_processamento = tempo_processamento
        self.data_termino = data_termino
        self.custo_antecipacao = custo_antecipacao
        self.custo_atraso = custo_atraso
class Entrada_Modelo:
    def __init__(self, nome_chapas, n, P, D, S, a, b):
        self.nome_chapas = nome_chapas
        self.n = n #numero de jobs
        self.P = P #vetor 
        self.D = D #vetor 
        self.S = S #matriz Setup
        self.a = a #vetor custo antecipacao dos jobs
        self.b = b #vetor custo atraso dos jobs
        self.M = 99999
    def __repr__(self):
        S_str = "\n".join(f"    {linha}" for linha in self.S)

        return (
            f"Entrada_Modelo(\n"
            f"  nome_chapas={self.nome_chapas},\n"
            f"  n={self.n},\n"
            f"  P={self.P},\n"
            f"  D={self.D},\n"
            f"  S=\n{S_str}\n"
            f"  a={self.a},\n"
            f"  b={self.b},\n"
            f"  M={self.M}\n"
            f")"
        )
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
    
    vetor_chapas = []
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
        vetor_chapas.append(job.nome_chapa)

    return Entrada_Modelo(vetor_chapas, n_jobs, vetor_tempo_processamento, vetor_data_termino, matriz_setup, vetor_custo_antecipacao, vetor_custo_atraso)
    

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
        jobs.append(Job(chapa.tipo, chapa.id, chapa.tempo_processamento, pedido.data_termino, pedido.custo_antecipacao, pedido.custo_atraso))

entrada = dados_entrada_modelo(jobs, dados_setups)

print(entrada)