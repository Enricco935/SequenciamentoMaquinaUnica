import sqlite3

DB = "producao.db"

def conectar():
    return sqlite3.connect(DB)

def criar_banco():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chapas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        tempo_processamento REAL NOT NULL
    )
    """)

    # Tabela de pedidos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_termino REAL,
        custo_atraso REAL,
        custo_antecipacao REAL,
        tempo_processamento REAL
    )
    """)

    # Tabela associativa entre pedidos e chapas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pedido_chapas (
        pedido_id INTEGER,
        chapa_id INTEGER,
        quantidade INTEGER NOT NULL DEFAULT 1,
        PRIMARY KEY (pedido_id, chapa_id),
        FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
        FOREIGN KEY (chapa_id) REFERENCES chapas(id)
    )
    """)

    # Tabela de setups entre chapas (origem -> destino)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS setups (
        origem_id INTEGER,
        destino_id INTEGER,
        tempo REAL NOT NULL DEFAULT 0,
        PRIMARY KEY (origem_id, destino_id),
        FOREIGN KEY (origem_id) REFERENCES chapas(id),
        FOREIGN KEY (destino_id) REFERENCES chapas(id)
    )
    """)

    cursor.execute("PRAGMA table_info(pedido_chapas)")
    colunas = [row[1] for row in cursor.fetchall()]
    if "quantidade" not in colunas:
        cursor.execute("ALTER TABLE pedido_chapas ADD COLUMN quantidade INTEGER NOT NULL DEFAULT 1")

    conn.commit()
    conn.close()


def inserir_chapa(nome, tempo_processamento):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO chapas (nome, tempo_processamento)
    VALUES (?, ?)
    """, (nome, tempo_processamento))

    conn.commit()
    chapa_id = cursor.lastrowid
    conn.close()

    # inicializar setups entre a nova chapa e as existentes
    inicializar_setups_para_chapa(chapa_id)

    return chapa_id


def listar_chapas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, nome, tempo_processamento
    FROM chapas
    """)

    dados = cursor.fetchall()

    conn.close()

    return dados

def deletar_chapa(chapa_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM chapas
        WHERE id = ?
        """,
        (chapa_id,)
    )

    conn.commit()
    conn.close()

    # remove setups e associações relacionadas
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM setups WHERE origem_id = ? OR destino_id = ?", (chapa_id, chapa_id))
    cursor.execute("DELETE FROM pedido_chapas WHERE chapa_id = ?", (chapa_id,))
    conn.commit()
    conn.close()


def inserir_pedido(data_termino, custo_atraso, custo_antecipacao, lista_chapas):
    conn = conectar()
    cursor = conn.cursor()

    # lista_chapas: list of tuples (chapa_id, quantidade)
    tempo_total = 0
    if lista_chapas:
        ids = [c for c, q in lista_chapas]
        placeholders = ",".join(["?"] * len(ids))
        cursor.execute(f"SELECT id, tempo_processamento FROM chapas WHERE id IN ({placeholders})", tuple(ids))
        tempos = {row[0]: row[1] for row in cursor.fetchall()}

        for chapa_id, quantidade in lista_chapas:
            tempo = tempos.get(chapa_id, 0)
            try:
                qty = int(quantidade)
            except Exception:
                qty = 1
            tempo_total += tempo * qty

    cursor.execute(
        """
        INSERT INTO pedidos (data_termino, custo_atraso, custo_antecipacao, tempo_processamento)
        VALUES (?, ?, ?, ?)
        """,
        (data_termino, custo_atraso, custo_antecipacao, tempo_total)
    )

    pedido_id = cursor.lastrowid

    # Inserir associações pedido_chapas com quantidade
    for chapa_id, quantidade in (lista_chapas or []):
        cursor.execute(
            """
            INSERT OR REPLACE INTO pedido_chapas (pedido_id, chapa_id, quantidade)
            VALUES (?, ?, ?)
            """,
            (pedido_id, chapa_id, quantidade)
        )

    conn.commit()
    conn.close()


def atualizar_setup(origem_id, destino_id, tempo):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO setups (origem_id, destino_id, tempo)
        VALUES (?, ?, ?)
        """,
        (origem_id, destino_id, tempo)
    )
    conn.commit()
    conn.close()


def listar_setups():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT origem_id, destino_id, tempo FROM setups")
    rows = cursor.fetchall()
    conn.close()
    return rows


def inicializar_setups_para_chapa(nova_chapa_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM chapas WHERE id != ?", (nova_chapa_id,))
    existentes = [row[0] for row in cursor.fetchall()]

    for eid in existentes:
        cursor.execute("INSERT OR IGNORE INTO setups (origem_id, destino_id, tempo) VALUES (?, ?, 0)", (nova_chapa_id, eid))
        cursor.execute("INSERT OR IGNORE INTO setups (origem_id, destino_id, tempo) VALUES (?, ?, 0)", (eid, nova_chapa_id))

    cursor.execute("INSERT OR IGNORE INTO setups (origem_id, destino_id, tempo) VALUES (?, ?, 0)", (nova_chapa_id, nova_chapa_id))

    conn.commit()
    conn.close()


def remover_setups_para_chapa(chapa_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM setups WHERE origem_id = ? OR destino_id = ?", (chapa_id, chapa_id))
    conn.commit()
    conn.close()


def listar_pedidos():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        p.id,
        p.data_termino,
        p.custo_antecipacao,
        p.custo_atraso,
        p.tempo_processamento,
        COUNT(pc.chapa_id) AS qtd_chapas_distintas,
        COALESCE(SUM(pc.quantidade), 0) AS qtd_total
    FROM pedidos p
    LEFT JOIN pedido_chapas pc ON p.id = pc.pedido_id
    GROUP BY p.id
    ORDER BY p.id DESC
    """)

    dados = cursor.fetchall()

    conn.close()

    return dados


def listar_chapas_por_pedido(pedido_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT c.id, c.nome, c.tempo_processamento, pc.quantidade
    FROM chapas c
    JOIN pedido_chapas pc ON c.id = pc.chapa_id
    WHERE pc.pedido_id = ?
    """, (pedido_id,))

    dados = cursor.fetchall()

    conn.close()

    return dados


def deletar_pedido(pedido_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM pedido_chapas
        WHERE pedido_id = ?
        """,
        (pedido_id,)
    )

    cursor.execute(
        """
        DELETE FROM pedidos
        WHERE id = ?
        """,
        (pedido_id,)
    )

    conn.commit()
    conn.close()