import tkinter as tk
from tkinter import ttk

from data_base import listar_chapas, inserir_chapa, deletar_chapa, inserir_pedido, listar_pedidos, deletar_pedido, listar_chapas_por_pedido, listar_setups, atualizar_setup

class InterfacePrincipal:

    def __init__(self, root):
        self.root = root

        self.root.title("Sequenciamento")
        self.root.geometry("500x300")

        self.criar_menu()

    def criar_menu(self):

        tk.Button(
            self.root,
            text="Chapas",
            width=30,
            command=self.abrir_janela_chapas
        ).pack(pady=10)

        tk.Button(
            self.root,
            text="Cadastrar Pedidos",
            width=30,
            command=self.abrir_janela_pedidos
        ).pack(pady=10)

        tk.Button(
            self.root,
            text="Cadastrar Setups",
            width=30
        ,
            command=self.abrir_janela_setups
        ).pack(pady=10)

        tk.Button(
            self.root,
            text="Resolver Modelo",
            width=30
        ).pack(pady=10)

    def abrir_janela_chapas(self):
        JanelaChapas(self.root)
    def abrir_janela_pedidos(self):
        JanelaPedidos(self.root)
    def abrir_janela_setups(self):
        JanelaSetups(self.root)

class JanelaChapas:

    def __init__(self, parent):

        self.window = tk.Toplevel(parent)

        self.window.title("Cadastro de Chapas")
        self.window.geometry("600x400")

        tk.Label(
            self.window,
            text="Nome"
        ).pack()

        self.nome = tk.Entry(self.window)
        self.nome.pack()

        tk.Label(
            self.window,
            text="Tempo de Processamento"
        ).pack()

        self.tempo = tk.Entry(self.window)
        self.tempo.pack()

        tk.Button(
            self.window,
            text="Salvar",
            command=self.salvar_chapa
        ).pack(pady=10)

        tk.Button(
            self.window,
            text="Excluir Selecionadas",
            command=self.excluir_chapa
        ).pack(pady=2)

        # Lista de chapas
        self.tabela = ttk.Treeview(
            self.window,
            columns=("id", "nome", "tempo"),
            show="headings",
            height=10
        )

        self.tabela.heading("id", text="ID")
        self.tabela.heading("nome", text="Nome")
        self.tabela.heading("tempo", text="Tempo")

        self.tabela.column("id", width=50)
        self.tabela.column("nome", width=250)
        self.tabela.column("tempo", width=150)

        self.tabela.pack(fill="both", expand=True, padx=10, pady=10)

        self.carregar_chapas()

    def carregar_chapas(self):
        # Limpa tabela existente
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        chapas = listar_chapas()

        for chapa in chapas:
            self.tabela.insert("", tk.END, values=chapa)

    def salvar_chapa(self):
        nome = self.nome.get().strip()
        tempo_txt = self.tempo.get().strip()

        if not nome or not tempo_txt:
            return

        try:
            tempo = float(tempo_txt)
        except ValueError:
            return

        inserir_chapa(nome, tempo)

        # Limpa entradas
        self.nome.delete(0, tk.END)
        self.tempo.delete(0, tk.END)

        # Recarrega a lista de chapas
        self.carregar_chapas()

    def excluir_chapa(self):
        selecionados = self.tabela.selection()
        if not selecionados:
            return

        for item in selecionados:
            valores = self.tabela.item(item, "values")
            if not valores:
                continue

            chapa_id = valores[0]
            try:
                chapa_id_int = int(chapa_id)
            except (ValueError, TypeError):
                continue

            # Deleta do banco
            deletar_chapa(chapa_id_int)

        # Recarrega a lista após exclusões
        self.carregar_chapas()


class QuantidadeDialog:
    def __init__(self, parent, chapas):
        # chapas: list of tuples (id, nome, tempo)
        self.top = tk.Toplevel(parent)
        self.top.title("Quantidades por Chapa")
        self.top.grab_set()

        self.entries = []
        for chapa in chapas:
            frame = tk.Frame(self.top)
            frame.pack(fill="x", padx=8, pady=4)
            tk.Label(frame, text=f"{chapa[0]} - {chapa[1]} ({chapa[2]})", width=50, anchor="w").pack(side="left")
            e = tk.Entry(frame, width=8)
            e.insert(0, "1")
            e.pack(side="right")
            self.entries.append(e)

        btn_frame = tk.Frame(self.top)
        btn_frame.pack(fill="x", pady=6)
        tk.Button(btn_frame, text="OK", command=self.on_ok).pack(side="right", padx=6)
        tk.Button(btn_frame, text="Cancelar", command=self.on_cancel).pack(side="right")

        self.result = None

    def on_ok(self):
        vals = []
        for e in self.entries:
            txt = e.get().strip()
            try:
                v = int(txt)
                if v < 1:
                    v = 1
            except Exception:
                v = 1
            vals.append(v)
        self.result = vals
        self.top.destroy()

    def on_cancel(self):
        self.result = None
        self.top.destroy()


class JanelaPedidos:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Cadastro de Pedidos")
        self.window.geometry("900x560")

        form_frame = tk.Frame(self.window)
        form_frame.pack(fill="x", padx=10, pady=8)

        tk.Label(form_frame, text="Data de Término").grid(row=0, column=0, sticky="w")
        self.data = tk.Entry(form_frame)
        self.data.grid(row=1, column=0, sticky="we", padx=(0, 10))

        tk.Label(form_frame, text="Custo Antecipação").grid(row=0, column=1, sticky="w")
        self.custo_ante = tk.Entry(form_frame)
        self.custo_ante.grid(row=1, column=1, sticky="we", padx=(0, 10))

        tk.Label(form_frame, text="Custo Atraso").grid(row=0, column=2, sticky="w")
        self.custo_atraso = tk.Entry(form_frame)
        self.custo_atraso.grid(row=1, column=2, sticky="we")

        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(2, weight=1)

        tk.Label(self.window, text="Selecionar Chapas").pack(anchor="w", padx=10)
        self.listbox_chapas = tk.Listbox(self.window, selectmode=tk.MULTIPLE, height=8)
        self.listbox_chapas.pack(fill="x", padx=10)

        btn_frame = tk.Frame(self.window)
        btn_frame.pack(fill="x", padx=10, pady=8)
        tk.Button(btn_frame, text="Salvar Pedido", command=self.salvar_pedido).pack(side="left")
        tk.Button(btn_frame, text="Excluir Pedido Selecionado", command=self.excluir_pedido).pack(side="left", padx=8)
        tk.Button(btn_frame, text="Ver Detalhes do Pedido", command=self.ver_detalhes_pedido).pack(side="left")

        table_frame = tk.Frame(self.window)
        table_frame.pack(fill="both", expand=True, padx=10, pady=8)

        self.tabela = ttk.Treeview(
            table_frame,
            columns=("id", "data", "custo_ante", "custo_atraso", "tempo", "qtd_chapas", "qtd_total"),
            show="headings",
            height=10
        )

        self.tabela.heading("id", text="ID")
        self.tabela.heading("data", text="Data término")
        self.tabela.heading("custo_ante", text="Custo antecip.")
        self.tabela.heading("custo_atraso", text="Custo atraso")
        self.tabela.heading("tempo", text="Tempo proc.")
        self.tabela.heading("qtd_chapas", text="Chapas distintas")
        self.tabela.heading("qtd_total", text="Qtd total")

        self.tabela.column("id", width=50)
        self.tabela.column("data", width=140)
        self.tabela.column("custo_ante", width=110)
        self.tabela.column("custo_atraso", width=110)
        self.tabela.column("tempo", width=100)
        self.tabela.column("qtd_chapas", width=100)
        self.tabela.column("qtd_total", width=100)

        self.tabela.pack(fill="both", expand=True)
        self.tabela.bind("<<TreeviewSelect>>", self.on_pedido_select)

        detail_label = tk.Label(self.window, text="Chapas no pedido selecionado")
        detail_label.pack(anchor="w", padx=10)

        self.tabela_detalhes = ttk.Treeview(
            self.window,
            columns=("id", "nome", "tempo", "quantidade", "subtotal"),
            show="headings",
            height=6
        )
        self.tabela_detalhes.heading("id", text="ID")
        self.tabela_detalhes.heading("nome", text="Nome")
        self.tabela_detalhes.heading("tempo", text="Tempo" )
        self.tabela_detalhes.heading("quantidade", text="Quantidade")
        self.tabela_detalhes.heading("subtotal", text="Subtotal")

        self.tabela_detalhes.column("id", width=50)
        self.tabela_detalhes.column("nome", width=180)
        self.tabela_detalhes.column("tempo", width=80)
        self.tabela_detalhes.column("quantidade", width=80)
        self.tabela_detalhes.column("subtotal", width=90)

        self.tabela_detalhes.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.carregar_chapas_disponiveis()
        self.carregar_pedidos()

    def carregar_chapas_disponiveis(self):
        self.listbox_chapas.delete(0, tk.END)
        self.chapas_disponiveis = listar_chapas()
        for chapa in self.chapas_disponiveis:
            texto = f"{chapa[0]} - {chapa[1]} ({chapa[2]})"
            self.listbox_chapas.insert(tk.END, texto)

    def carregar_pedidos(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        pedidos = listar_pedidos()
        for ped in pedidos:
            # ped: (id, data_termino, custo_antecipacao, custo_atraso, tempo_processamento, qtd_chapas, qtd_total)
            self.tabela.insert("", tk.END, values=ped)

        self.limpar_detalhes()

    def salvar_pedido(self):
        data_txt = self.data.get().strip()
        custo_ante_txt = self.custo_ante.get().strip()
        custo_atraso_txt = self.custo_atraso.get().strip()

        try:
            custo_ante = float(custo_ante_txt) if custo_ante_txt else 0.0
            custo_atraso = float(custo_atraso_txt) if custo_atraso_txt else 0.0
            tempo = float(data_txt)
        except ValueError:
            return

        selecionados = self.listbox_chapas.curselection()
        lista_chapas = []
        if selecionados:
            chapas_selecionadas = [self.chapas_disponiveis[idx] for idx in selecionados]
            dlg = QuantidadeDialog(self.window, chapas_selecionadas)
            self.window.wait_window(dlg.top)
            if dlg.result is None:
                return

            for chapa, qty in zip(chapas_selecionadas, dlg.result):
                try:
                    chapa_id = int(chapa[0])
                    q = int(qty)
                    if q < 1:
                        q = 1
                except Exception:
                    continue
                lista_chapas.append((chapa_id, q))

        inserir_pedido(tempo, custo_atraso, custo_ante, lista_chapas)

        self.data.delete(0, tk.END)
        self.custo_ante.delete(0, tk.END)
        self.custo_atraso.delete(0, tk.END)
        self.listbox_chapas.selection_clear(0, tk.END)

        self.carregar_chapas_disponiveis()
        self.carregar_pedidos()

    def excluir_pedido(self):
        selecionados = self.tabela.selection()
        if not selecionados:
            return

        for item in selecionados:
            valores = self.tabela.item(item, "values")
            if not valores:
                continue
            try:
                pedido_id = int(valores[0])
            except Exception:
                continue
            deletar_pedido(pedido_id)

        self.carregar_pedidos()

    def on_pedido_select(self, event):
        self.ver_detalhes_pedido()

    def ver_detalhes_pedido(self):
        selecionados = self.tabela.selection()
        if not selecionados:
            self.limpar_detalhes()
            return

        item = selecionados[0]
        valores = self.tabela.item(item, "values")
        if not valores:
            self.limpar_detalhes()
            return

        try:
            pedido_id = int(valores[0])
        except Exception:
            self.limpar_detalhes()
            return

        setup_dict = {
                (origem, destino): tempo
                for origem, destino, tempo in listar_setups()
            }



        detalhes = listar_chapas_por_pedido(pedido_id)
        self.tabela_detalhes.delete(*self.tabela_detalhes.get_children())
        for i, (chapa_id, nome, tempo, quantidade) in enumerate(detalhes):

            subtotal = float(tempo) * int(quantidade)

            if i < len(detalhes) - 1:
                prox_chapa_id = detalhes[i + 1][0]
                subtotal += setup_dict.get(
                    (chapa_id, prox_chapa_id),
                    0
                )

            self.tabela_detalhes.insert(
                "",
                tk.END,
                values=(
                    chapa_id,
                    nome,
                    tempo,
                    quantidade,
                    subtotal
                )
            )

    def limpar_detalhes(self):
        self.tabela_detalhes.delete(*self.tabela_detalhes.get_children())


class JanelaSetups:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Configurar Setups")
        self.window.geometry("900x600")

        self.chapas = listar_chapas()

        canvas = tk.Canvas(self.window)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_v = tk.Scrollbar(self.window, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_h = tk.Scrollbar(self.window, orient=tk.HORIZONTAL, command=canvas.xview)
        scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)

        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor='nw')

        setups = { (o,d):t for o,d,t in listar_setups() }
        self.entries = {}

        # headers
        tk.Label(frame, text="").grid(row=0, column=0, padx=4, pady=4)
        for j, chapa_col in enumerate(self.chapas, start=1):
            tk.Label(frame, text=f"{chapa_col[0]}\n{chapa_col[1]}", borderwidth=1, relief="ridge", width=12).grid(row=0, column=j, padx=2, pady=2)

        for i, chapa_row in enumerate(self.chapas, start=1):
            tk.Label(frame, text=f"{chapa_row[0]} {chapa_row[1]}", borderwidth=1, relief="ridge", width=18).grid(row=i, column=0, padx=2, pady=2)
            for j, chapa_col in enumerate(self.chapas, start=1):
                origem = chapa_row[0]
                destino = chapa_col[0]
                key = (origem, destino)
                val = setups.get(key, 0)
                e = tk.Entry(frame, width=10)
                if origem == destino:
                    e.insert(0, "0")
                    e.configure(state="disabled")
                else:
                    e.insert(0, str(val))
                e.grid(row=i, column=j, padx=2, pady=2)
                self.entries[key] = e

        frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox('all'))

        btn_frame = tk.Frame(self.window)
        btn_frame.pack(fill="x", pady=6)
        tk.Button(btn_frame, text="Salvar Setups", command=self.salvar_setups).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Fechar", command=self.window.destroy).pack(side="left")

    def salvar_setups(self):
        for (origem, destino), entry in self.entries.items():
            if origem == destino:
                continue
            txt = entry.get().strip()
            try:
                tempo = float(txt) if txt else 0.0
            except ValueError:
                tempo = 0.0
            atualizar_setup(origem, destino, tempo)

        self.window.destroy()
