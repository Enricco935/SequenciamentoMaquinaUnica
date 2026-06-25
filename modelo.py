from pulp import *
import dados as dt


# Cria o problema
prob = LpProblem("Sequenciamento_Maquina", LpMinimize)

n = dt.entrada.n  # número de jobs
P = dt.entrada.P  # tempo processamento
D = dt.entrada.D  # data termino
a = dt.entrada.a  # custo antecipacao
b = dt.entrada.b  # custo atraso
S = dt.entrada.S  # setup times
M = dt.entrada.M  # big M  

# Variáveis
s = []
y = []
e = []
t = []

for i in range(n):
    s.append(LpVariable(f"s{i}", lowBound=0,cat='Continuous'))
    e.append(LpVariable(f"e{i}", lowBound=0,cat='Continuous'))   
    t.append(LpVariable(f"t{i}", lowBound=0,cat='Continuous'))
    y.append([])
    for j in range(n):
        y[i].append(LpVariable(f"y_{i}_{j}", cat='Binary'))
        

variaveis = dt.Variaveis_decisao(s, y, e, t, None)

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
        prob += y[i][j] + y[j][i] <= 1
    prob += s[i]+P[i]+e[i]-t[i] == D[i]
        
#a
# Resolve
prob.solve()

for i in range(n):
    print(f"Job {i}: Início = {value(s[i]):.2f}, Término = {value(s[i]) + P[i]:.2f}")


#Quando nois pegar pra fazer esse trem junto...
