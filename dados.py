class Pedido:
    def __init__(self, qtd_lote, qtd_chapas, custo_antecipacao, custo_atraso):
        self.qtd_lote = qtd_lote
        self.qtd_chapas = qtd_chapas
        self.tempo_processamento_chapa = [None] * qtd_chapas
        
        self.custo_antecipacao = custo_antecipacao
        self.custo_atraso = custo_atraso
        self.qtd_jobs = qtd_chapas * qtd_lote
        self.prazo_entrega_job = [[None for j in range(qtd_chapas)] for i in range(qtd_lote)]
        self.setup_jobs = []
        self.tempo_processamento_job = []
