import tkinter as tk
from tkinter import messagebox
from tksheet import Sheet

from dados import Pedido
from matrizes import converter_matriz_para_int

def imprimir_matriz(matriz):
    for i in matriz:
        for j in i:
            print(j, end=" ")
        print()

# Funcao antiga para entrada via terminal.
# Nao e usada pela interface grafica atual.

# def ler_pedido():
#     qtd_lote = int(input("Quantidade de pedidos diferentes: "))
#     qtd_chapas = int(input("Quantidade de chapas diferentes: "))
#     custo_antecipacao = float(input("Custo de antecipacao: R$"))
#     custo_atraso = float(input("Custo de atraso: R$"))

#     pedido = Pedido(qtd_lote, qtd_chapas, custo_antecipacao, custo_atraso)

#     for i in range(qtd_chapas):
#         pedido.tempo_processamento_chapa[i] = int(
#             input(f"Tempo de processamento da chapa {i + 1}: ")
#         )

#     for i in range(pedido.qtd_lote):
#         valor = int(input(f"Prazo de entrega do lote {i+1}: "))
#         for  j in range(pedido.qtd_chapas):
#             pedido.prazo_entrega_job[i][j] =  valor
    
#     return pedido

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
