from pathlib import Path


def nomes_jobs(pedido):
    nomes = []

    for i in range(pedido.qtd_lote):
        for j in range(pedido.qtd_chapas):
            nomes.append(f"L{i + 1}C{j + 1}")

    return nomes


def gerar_dat(pedido, caminho="dados.dat"):
    caminho = Path(caminho)
    jobs = nomes_jobs(pedido)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    with caminho.open("w", encoding="utf-8") as arq:
        arq.write("set JOBS :=\n")
        for i in range(pedido.qtd_lote):
            linha = []
            for j in range(pedido.qtd_chapas):
                linha.append(f"L{i + 1}C{j + 1}")
            arq.write(" ".join(linha) + "\n")
        arq.write(";\n\n")

        arq.write(f"param a := {pedido.custo_antecipacao};\n")
        arq.write(f"param b := {pedido.custo_atraso};\n\n")

        arq.write("param p :=\n")
        for i in range(pedido.qtd_lote):
            linha = []
            for j in range(pedido.qtd_chapas):
                nome_job = f"L{i + 1}C{j + 1}"
                tempo = pedido.tempo_processamento_job[i][j]
                linha.append(f"{nome_job} {tempo}")
            arq.write("  ".join(linha) + "\n")
        arq.write(";\n\n")

        arq.write("param d :=\n")
        for i in range(pedido.qtd_lote):
            linha = []
            for j in range(pedido.qtd_chapas):
                nome_job = f"L{i + 1}C{j + 1}"
                prazo = pedido.prazo_entrega_job[i][j]
                linha.append(f"{nome_job} {prazo}")
            arq.write("  ".join(linha) + "\n")
        arq.write(";\n\n")

        arq.write("param setup :\n")
        arq.write("       " + " ".join(jobs) + " :=\n")

        for i, nome_linha in enumerate(jobs):
            valores = []
            for j in range(len(jobs)):
                valores.append(str(pedido.setup_jobs[i][j]))
            arq.write(f"{nome_linha}    " + "    ".join(valores) + "\n")

        arq.write(";\n\n")
        arq.write("end;\n")

    return caminho
