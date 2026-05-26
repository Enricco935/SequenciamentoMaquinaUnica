set JOBS;

param a;		 # custo antecipacao
param b;		 # custo atraso
param p{JOBS};           # tempo de processamento
param d{JOBS};           # prazo maximo
param setup{JOBS,JOBS};  # tempo de setup

var S{JOBS} >= 0;        # inicio
var T{JOBS} >= 0;        # atraso
var E{JOBS} >= 0;	 # adiantamento
var x{JOBS,JOBS} binary; # ordem

minimize Custo: sum{i in JOBS} (T[i]*b + E[i]*a);

subject to
c1{i in JOBS, j in JOBS: i != j}:  S[j] - S[i] - (10000 + setup[i,j])* x[i,j] >= p[i] - 10000; 
	
c2{i in JOBS, j in JOBS:i < j}: x[i,j] + x[j,i] = 1;

c3{i in JOBS}: S[i] + p[i] + E[i] - T[i] = d[i];

solve;

printf {i in JOBS} "%s %f\n", i, S[i];



