from dataclasses import dataclass

try:
    import pulp
except ImportError:
    pulp = None

from gerador_dat import nomes_jobs


@dataclass
class ResultadoPulp:
    status: str
    status_pulp: int
    objetivo: float | None
    inicios: dict[str, float]
    atrasos: dict[str, float]
    antecipacoes: dict[str, float]
    mensagem: str


def _valor_variavel(variavel):
    valor = pulp.value(variavel)
    if valor is None:
        return 0.0
    return float(valor)


def resolver_pedido_com_pulp(pedido, limite_tempo=120):
    if pulp is None:
        raise ImportError("PuLP nao esta instalado.")

    jobs = nomes_jobs(pedido)
    tempos = {
        job: pedido.tempo_processamento_job[i][j]
        for i in range(pedido.qtd_lote)
        for j, job in enumerate(jobs[i * pedido.qtd_chapas : (i + 1) * pedido.qtd_chapas])
    }
    prazos = {
        job: pedido.prazo_entrega_job[i][j]
        for i in range(pedido.qtd_lote)
        for j, job in enumerate(jobs[i * pedido.qtd_chapas : (i + 1) * pedido.qtd_chapas])
    }
    setup = {
        (job_i, job_j): pedido.setup_jobs[i][j]
        for i, job_i in enumerate(jobs)
        for j, job_j in enumerate(jobs)
    }

    maior_setup = max(setup.values(), default=0)
    horizonte = sum(tempos.values()) + maior_setup * max(len(jobs) - 1, 0)
    big_m = max(10000, horizonte + maior_setup + max(prazos.values(), default=0))

    modelo = pulp.LpProblem("Sequenciamento_Maquina_Unica", pulp.LpMinimize)

    inicio = pulp.LpVariable.dicts("S", jobs, lowBound=0)
    atraso = pulp.LpVariable.dicts("T", jobs, lowBound=0)
    antecipacao = pulp.LpVariable.dicts("E", jobs, lowBound=0)
    ordem = pulp.LpVariable.dicts("x", (jobs, jobs), cat=pulp.LpBinary)

    modelo += pulp.lpSum(
        atraso[job] * pedido.custo_atraso + antecipacao[job] * pedido.custo_antecipacao
        for job in jobs
    )

    for job_i in jobs:
        for job_j in jobs:
            if job_i == job_j:
                continue
            modelo += (
                inicio[job_j]
                >= inicio[job_i]
                + tempos[job_i]
                + setup[(job_i, job_j)]
                - big_m * (1 - ordem[job_i][job_j])
            )

    for pos_i, job_i in enumerate(jobs):
        for job_j in jobs[pos_i + 1 :]:
            modelo += ordem[job_i][job_j] + ordem[job_j][job_i] == 1

    for job in jobs:
        modelo += inicio[job] + tempos[job] + antecipacao[job] - atraso[job] == prazos[job]

    solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=limite_tempo)
    status_pulp = modelo.solve(solver)
    status = pulp.LpStatus.get(status_pulp, "Nao identificado")
    objetivo = pulp.value(modelo.objective)

    return ResultadoPulp(
        status=status,
        status_pulp=status_pulp,
        objetivo=None if objetivo is None else float(objetivo),
        inicios={job: _valor_variavel(inicio[job]) for job in jobs},
        atrasos={job: _valor_variavel(atraso[job]) for job in jobs},
        antecipacoes={job: _valor_variavel(antecipacao[job]) for job in jobs},
        mensagem=f"PuLP/CBC finalizou com status: {status}",
    )
