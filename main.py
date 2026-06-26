import tkinter as tk
from interface import InterfacePrincipal
from data_base import criar_banco


criar_banco()

root = tk.Tk()

app = InterfacePrincipal(root)

root.mainloop()
