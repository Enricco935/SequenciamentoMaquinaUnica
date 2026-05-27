import tkinter as tk
from tkinter import messagebox
from tksheet import Sheet

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

def imprimir_matriz(matriz):
    for i in matriz:
        for j in i:
            print(j, end=" ")
        print()

def ler_pedido():
    qtd_lote = int(input("Quantidade de pedidos diferentes: "))
    qtd_chapas = int(input("Quantidade de chapas diferentes: "))
    custo_antecipacao = float(input("Custo de antecipação: R$"))
    custo_atraso = float(input("Custo de atraso: R$"))

    pedido = Pedido(qtd_lote, qtd_chapas, custo_antecipacao, custo_atraso)

    for i in range(qtd_chapas):
        pedido.tempo_processamento_chapa[i] = int(
            input(f"Tempo de processamento da chapa {i + 1}: ")
        )

    for i in range(pedido.qtd_lote):
        valor = int(input(f"Prazo de entrega do lote {i+1}: "))
        for  j in range(pedido.qtd_chapas):
            pedido.prazo_entrega_job[i][j] =  valor
    
    return pedido

def converter_matriz_para_int(matriz):
    matriz_convertida = []

    for i, linha in enumerate(matriz):
        linha_convertida = []
        for j, valor in enumerate(linha):
            if valor == "" or valor is None:
                raise ValueError(f"Celula vazia na linha {i + 1}, coluna {j + 1}")

            try:
                linha_convertida.append(int(valor))
            except ValueError:
                raise ValueError(
                    f"Valor invalido na linha {i + 1}, coluna {j + 1}: {valor}"
                )

        matriz_convertida.append(linha_convertida)

    return matriz_convertida

def exibir_janela_matriz(titulo, linhas, colunas):
    dados = [["" for j in range(colunas)] for i in range(linhas)]
    matriz = None

    root = tk.Tk()
    root.title(titulo)

    sheet = Sheet(
        root,
        data=dados,
        width=900,
        height=400
    )

    sheet.enable_bindings()
    sheet.pack(fill="both", expand=True)

    def salvar():
        nonlocal matriz
        dados_digitados = sheet.get_sheet_data()

        try:
            matriz = converter_matriz_para_int(dados_digitados)
        except ValueError as erro:
            messagebox.showerror("Erro na matriz", str(erro))
            return

        root.destroy()

    btn = tk.Button(root, text="Salvar", command=salvar)
    btn.pack()

    root.mainloop()

    return matriz

def preenche_matriz_setup_completa(pedido, setup):
    tamanho = pedido.qtd_lote * pedido.qtd_chapas
    Setup = [[0 for j in range(tamanho)] for i in range(tamanho)]

    for i in range(tamanho):
        for j in range(tamanho):
            Setup[i][j] = setup[i % pedido.qtd_chapas][j % pedido.qtd_chapas]

    return Setup

def multiplicar_matriz_jobs(matriz, vetor):
    for i in range(len(matriz)):
        for j in range(len(matriz[i])):
            matriz[i][j] = matriz[i][j] * vetor[j]
    return matriz

pedido = ler_pedido()

setup = exibir_janela_matriz(
    "Preencher matriz de setup",
    pedido.qtd_chapas,
    pedido.qtd_chapas
)

matriz_jobs = exibir_janela_matriz(
    "Preencher matriz de jobs",
    pedido.qtd_lote,
    pedido.qtd_chapas
)

pedido.setup_jobs = preenche_matriz_setup_completa(pedido, setup)

print("Matriz de setup digitada:")
imprimir_matriz(setup)

print("Matriz de jobs digitada:")
imprimir_matriz(matriz_jobs)

print("Matriz de setup expandida:")
imprimir_matriz(pedido.setup_jobs)

print("-" * 50)

pedido.tempo_processamento_job = multiplicar_matriz_jobs(matriz_jobs, pedido.tempo_processamento_chapa)

print("Matriz de jobs multiplicada por tempo de processamento:")
imprimir_matriz(matriz_jobs)
print(pedido.tempo_processamento_chapa)
print(pedido.prazo_entrega_job)