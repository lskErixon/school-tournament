import tkinter as tk
from tkinter import ttk

from ui.screens.home_screen import HomeScreen

class App(tk.Tk):
    def __init__(self, db):
        super().__init__()
        self.db = db

        self.title("School Tournament (D1)")
        self.geometry("1100x650")
        self.minsize(950, 600)

        root = ttk.Frame(self)
        root.pack(fill="both", expand=True)

        HomeScreen(root, self).pack(fill="both", expand=True)
