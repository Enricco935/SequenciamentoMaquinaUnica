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
