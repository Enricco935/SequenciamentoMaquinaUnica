from pulp import *
import dados as dt


def resolver(pedido_id=None):
    entrada = dt.carregar_entrada(pedido_id)

    # Cria o problema
    prob = LpProblem("Sequenciamento_Maquina", LpMinimize)

    n = entrada.n  # número de jobs
    P = entrada.P  # tempo processamento
    D = entrada.D  # data termino
    a = entrada.a  # custo antecipacao
    b = entrada.b  # custo atraso
    S = entrada.S  # setup times
    M = entrada.M  # big M
    pedido_ids = entrada.pedido_ids

    # Variáveis
    s = []
    y = []
    e = []
    t = []

    for i in range(n):
        s.append(LpVariable(f"s{i}", lowBound=0, cat='Continuous'))
        e.append(LpVariable(f"e{i}", lowBound=0, cat='Continuous'))
        t.append(LpVariable(f"t{i}", lowBound=0, cat='Continuous'))
        y.append([])
        for j in range(n):
            y[i].append(LpVariable(f"y_{i}_{j}", cat='Binary'))

    # Função objetivo
    obj = 0

    for i in range(n):
        obj += a[i] * e[i] + b[i] * t[i]

    prob += obj

    # Restrições

    for i in range(n):

        for j in range(n):
            if i == j:
                continue

            prob += s[j] - s[i] - ((M + S[i][j]) * y[i][j]) >= P[i] - M
            prob += y[i][j] + y[j][i] == 1
        prob += s[i] + P[i] + e[i] - t[i] == D[i]

    # Resolve
    prob.solve(PULP_CBC_CMD(msg=0))

    # Monta o resultado em ordem de produção
    jobs = []
    for i in range(n):
        jobs.append({
            "nome": entrada.nome_chapas[i],
            "pedido": pedido_ids[i],
            "inicio": value(s[i]),
            "fim": value(s[i]) + P[i],
            "prazo": D[i],
            "antecipacao": value(e[i]),
            "atraso": value(t[i]),
        })
    jobs.sort(key=lambda j: j["inicio"])

    return {
        "status": LpStatus[prob.status],
        "custo": value(obj),
        "custo_antecipacao": sum(a[i] * value(e[i]) for i in range(n)),
        "custo_atraso": sum(b[i] * value(t[i]) for i in range(n)),
        "jobs": jobs,
    }
