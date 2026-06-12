import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from tksheet import Sheet

from dados import Pedido
from gerador_dat import gerar_dat
from matrizes import (
    converter_matriz_para_int,
    multiplicar_matriz_jobs,
    preenche_matriz_setup_completa,
)
from solver_pulp import resolver_pedido_com_pulp


PASTA_PROJETO = Path(__file__).resolve().parent
PASTA_PULP = PASTA_PROJETO / "pulp"
CAMINHO_DAT = PASTA_PULP / "sq.dat"
CAMINHO_RELATORIO = PASTA_PROJETO / "relatorio_resultado.txt"


def formatar_numero(valor):
    if valor == int(valor):
        return str(int(valor))
    return f"{valor:.2f}"


def montar_resumo_otimo(pedido, caminho_dat, resultado, matriz_quantidades):
    if resultado.objetivo is None:
        objetivo = "Nao identificado"
    else:
        objetivo = formatar_numero(resultado.objetivo)

    # Ordena os jobs pela ordem em que comecam na maquina.
    sequencia = []
    for job in resultado.inicios:
        sequencia.append((resultado.inicios[job], job))
    sequencia.sort()

    total_antecipacao = sum(resultado.antecipacoes.values())
    total_atraso = sum(resultado.atrasos.values())
    custo_antecipacao = total_antecipacao * pedido.custo_antecipacao
    custo_atraso = total_atraso * pedido.custo_atraso

    # Soma quanto produzir de cada chapa, somando todos os lotes.
    quantidades_por_chapa = [0] * pedido.qtd_chapas
    for linha in matriz_quantidades:
        for coluna in range(len(linha)):
            quantidades_por_chapa[coluna] += linha[coluna]

    linhas = [
        "RELATORIO DE PROGRAMACAO DA PRODUCAO",
        "",
        "Resumo da recomendacao",
        "Foi encontrada a melhor programacao possivel para os dados informados.",
        f"Custo total estimado da programacao: R$ {objetivo}",
        f"Custo por antecipacao: R$ {formatar_numero(custo_antecipacao)}",
        f"Custo por atraso: R$ {formatar_numero(custo_atraso)}",
        f"Total de tempo antecipado: {formatar_numero(total_antecipacao)}",
        f"Total de tempo em atraso: {formatar_numero(total_atraso)}",
        "",
        "Quantidade recomendada por item",
    ]

    for indice in range(pedido.qtd_chapas):
        quantidade = quantidades_por_chapa[indice]
        linhas.append(f"Chapa {indice + 1}: produzir {quantidade} unidade(s).")

    linhas.append("")
    linhas.append("Decisoes calculadas pelo sistema")

    posicao = 1
    for inicio, job in sequencia:
        partes = job[1:].split("C")          # "L1C2" -> ["1", "2"]
        lote = int(partes[0]) - 1
        chapa = int(partes[1]) - 1

        quantidade = matriz_quantidades[lote][chapa]
        tempo = pedido.tempo_processamento_job[lote][chapa]
        prazo = pedido.prazo_entrega_job[lote][chapa]
        termino = inicio + tempo
        atraso = resultado.atrasos[job]
        antecipacao = resultado.antecipacoes[job]

        situacao = "no prazo"
        if atraso > 0:
            situacao = f"com atraso de {formatar_numero(atraso)}"
        elif antecipacao > 0:
            situacao = f"com antecipacao de {formatar_numero(antecipacao)}"

        linhas.append(
            f"{posicao}. Lote {partes[0]} - Chapa {partes[1]}: produzir {quantidade} unidade(s), "
            f"iniciar no tempo {formatar_numero(inicio)}, "
            f"terminar no tempo {formatar_numero(termino)}, "
            f"prazo {formatar_numero(prazo)} ({situacao})."
        )
        posicao += 1

    linhas.append("")
    linhas.append(f"Relatorio salvo em: {CAMINHO_RELATORIO}")
    linhas.append(f"Arquivo de dados usado no calculo: {caminho_dat}")

    return "\n".join(linhas)


def atualizar_texto(widget, conteudo):
    widget.configure(state="normal")
    widget.delete("1.0", tk.END)
    widget.insert(tk.END, conteudo)
    widget.configure(state="disabled")


def criar_tabela(pai, titulo, linhas, colunas, altura=150,
                 nomes_linhas=None, nomes_colunas=None):
    frame = ttk.LabelFrame(pai, text=titulo, padding=8)
    frame.pack(fill="both", expand=True, pady=6)
    dados = [["" for _ in range(colunas)] for _ in range(linhas)]
    sheet = Sheet(frame, data=dados, height=altura,
                  headers=nomes_colunas, row_index=nomes_linhas)
    sheet.enable_bindings()
    sheet.pack(fill="both", expand=True)
    return sheet


def configurar_diagonal_setup(sheet, tamanho):
    celulas = []
    for i in range(tamanho):
        celulas.append((i, i))
        sheet.set_cell_data(i, i, 0, redraw=False)
    sheet.readonly_cells(cells=celulas, readonly=True, redraw=False)
    sheet.highlight_cells(cells=celulas, bg="#e8e8e8", fg="#555555", redraw=True)


def abrir_interface():
    root = tk.Tk()
    root.title("Sequenciamento em Maquina Unica")
    root.geometry("1050x720")

    sheets = {}
    entradas = {}

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    aba_dados = ttk.Frame(notebook, padding=12)
    aba_matrizes = ttk.Frame(notebook, padding=12)
    aba_resultado = ttk.Frame(notebook, padding=12)
    aba_dat = ttk.Frame(notebook, padding=12)

    notebook.add(aba_dados, text="Dados gerais")
    notebook.add(aba_matrizes, text="Matrizes")
    notebook.add(aba_resultado, text="Resultado otimo")
    notebook.add(aba_dat, text="Arquivo .dat")

    resultado_texto = tk.Text(aba_resultado, height=25, wrap="word")
    resultado_texto.pack(fill="both", expand=True)

    dat_texto = tk.Text(aba_dat, height=25, wrap="none")
    dat_texto.pack(fill="both", expand=True)

    def adicionar_campo(linha, texto, nome):
        ttk.Label(aba_dados, text=texto).grid(row=linha, column=0, sticky="w", pady=6)
        entrada = ttk.Entry(aba_dados, width=20)
        entrada.grid(row=linha, column=1, sticky="w", pady=6, padx=(8, 0))
        entradas[nome] = entrada

    adicionar_campo(0, "Quantidade de lotes", "qtd_lote")
    adicionar_campo(1, "Quantidade de chapas", "qtd_chapas")
    adicionar_campo(2, "Custo de antecipacao", "custo_antecipacao")
    adicionar_campo(3, "Custo de atraso", "custo_atraso")

    def ler_dados_gerais():
        try:
            qtd_lote = int(entradas["qtd_lote"].get())
            qtd_chapas = int(entradas["qtd_chapas"].get())
            custo_antecipacao = float(entradas["custo_antecipacao"].get())
            custo_atraso = float(entradas["custo_atraso"].get())
        except ValueError:
            messagebox.showerror("Erro", "Preencha os dados gerais com numeros validos.")
            return None
        return qtd_lote, qtd_chapas, custo_antecipacao, custo_atraso

    def obter_matriz(nome):
        return converter_matriz_para_int(sheets[nome].get_sheet_data())

    def gerar_tabelas():
        dados_gerais = ler_dados_gerais()
        if dados_gerais is None:
            return

        qtd_lote, qtd_chapas, _, _ = dados_gerais

        for widget in aba_matrizes.winfo_children():
            widget.destroy()
        sheets.clear()

        chapas = [f"Chapa {i + 1}" for i in range(qtd_chapas)]
        lotes = [f"Lote {i + 1}" for i in range(qtd_lote)]

        sheets["tempo_processamento"] = criar_tabela(
            aba_matrizes, "Tempo de processamento por chapa",
            1, qtd_chapas, altura=90,
            nomes_linhas=["Tempo"], nomes_colunas=chapas,
        )
        sheets["prazo_entrega"] = criar_tabela(
            aba_matrizes, "Prazo de entrega por lote",
            qtd_lote, 1, altura=120,
            nomes_linhas=lotes, nomes_colunas=["Prazo"],
        )
        sheets["setup"] = criar_tabela(
            aba_matrizes, "Matriz de setup",
            qtd_chapas, qtd_chapas,
            nomes_linhas=chapas, nomes_colunas=chapas,
        )
        configurar_diagonal_setup(sheets["setup"], qtd_chapas)

        sheets["jobs"] = criar_tabela(
            aba_matrizes, "Quantidade de chapas por lote",
            qtd_lote, qtd_chapas,
            nomes_linhas=lotes, nomes_colunas=chapas,
        )

        ttk.Button(aba_matrizes, text="Resolver", command=resolver).pack(anchor="e", pady=(8, 0))
        notebook.select(aba_matrizes)

    def resolver():
        dados_gerais = ler_dados_gerais()
        if dados_gerais is None:
            return

        qtd_lote, qtd_chapas, custo_antecipacao, custo_atraso = dados_gerais

        try:
            tempo_processamento = obter_matriz("tempo_processamento")[0]
            prazo_entrega = obter_matriz("prazo_entrega")
            setup = obter_matriz("setup")
            matriz_jobs = obter_matriz("jobs")
        except ValueError as erro:
            messagebox.showerror("Erro nos dados", str(erro))
            return

        # Zera a diagonal do setup (uma chapa para ela mesma nao tem troca).
        for i in range(len(setup)):
            setup[i][i] = 0

        # Guarda as quantidades originais (a matriz e alterada logo abaixo).
        matriz_quantidades = [list(linha) for linha in matriz_jobs]

        pedido = Pedido(qtd_lote, qtd_chapas, custo_antecipacao, custo_atraso)
        pedido.tempo_processamento_chapa = tempo_processamento

        for i in range(pedido.qtd_lote):
            valor = prazo_entrega[i][0]
            for j in range(pedido.qtd_chapas):
                pedido.prazo_entrega_job[i][j] = valor

        pedido.setup_jobs = preenche_matriz_setup_completa(pedido, setup)
        pedido.tempo_processamento_job = multiplicar_matriz_jobs(
            matriz_jobs, pedido.tempo_processamento_chapa,
        )

        PASTA_PULP.mkdir(exist_ok=True)
        caminho_dat = gerar_dat(pedido, CAMINHO_DAT)
        atualizar_texto(dat_texto, caminho_dat.read_text(encoding="utf-8"))

        resultado = resolver_pedido_com_pulp(pedido)

        if resultado.status != "Optimal":
            atualizar_texto(
                resultado_texto,
                "O PuLP/CBC nao confirmou uma solucao otima.\n\n"
                f"Status: {resultado.status}\n\n"
                f"{resultado.mensagem}",
            )
            notebook.select(aba_resultado)
            return

        relatorio = montar_resumo_otimo(pedido, caminho_dat, resultado, matriz_quantidades)
        CAMINHO_RELATORIO.write_text(relatorio, encoding="utf-8")
        atualizar_texto(resultado_texto, relatorio)
        notebook.select(aba_resultado)

    ttk.Button(aba_dados, text="Gerar tabelas", command=gerar_tabelas).grid(
        row=4, column=0, columnspan=2, sticky="w", pady=(14, 0)
    )

    root.mainloop()
