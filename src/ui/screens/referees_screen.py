from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from src.models.referee import Referee
from src.repositories.referee_repository import RefereeRepository
from src.db_mysql import DbError


class RefereeCreateDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Create referee")
        self.resizable(False, False)
        self.result: Referee | None = None

        self.transient(parent)
        self.grab_set()

        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)

        ttk.Label(root, text="Full name").grid(row=0, column=0, sticky="w")
        self.var_name = tk.StringVar()
        ttk.Entry(root, textvariable=self.var_name, width=40).grid(row=0, column=1)

        ttk.Label(root, text="Email").grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.var_email = tk.StringVar()
        ttk.Entry(root, textvariable=self.var_email, width=40).grid(row=1, column=1, pady=(6, 0))

        ttk.Label(root, text="Level").grid(row=2, column=0, sticky="w", pady=(6, 0))
        self.var_level = tk.StringVar(value="student")
        ttk.Combobox(
            root,
            textvariable=self.var_level,
            values=("student", "teacher", "external"),
            state="readonly",
            width=37,
        ).grid(row=2, column=1, pady=(6, 0))

        self.var_active = tk.IntVar(value=1)
        ttk.Checkbutton(root, text="Active", variable=self.var_active).grid(row=3, column=1, sticky="w", pady=(6, 0))

        btns = ttk.Frame(root)
        btns.grid(row=4, column=0, columnspan=2, sticky="e", pady=(10, 0))

        ttk.Button(btns, text="Cancel", command=self._cancel).pack(side="right")
        ttk.Button(btns, text="Create", command=self._save).pack(side="right", padx=(0, 8))

        self.bind("<Escape>", lambda _: self._cancel())
        self.bind("<Return>", lambda _: self._save())

    def _cancel(self):
        self.destroy()

    def _save(self):
        name = self.var_name.get().strip()
        email = self.var_email.get().strip()
        level = self.var_level.get()
        active = bool(self.var_active.get())

        if not name:
            messagebox.showerror("Error", "Full name is required")
            return

        self.result = Referee(
            referee_id=None,
            full_name=name,
            email=email,
            level=level,
            active=active,
        )
        self.destroy()


class RefereesScreen(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=10)
        self.app = app
        self.repo = RefereeRepository(app.db)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Referees", font=("Arial", 20, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Button(header, text="Add referee", command=self.create_referee).grid(row=0, column=1, sticky="e")

        self.tree = ttk.Treeview(
            self,
            columns=("id", "name", "email", "level", "active"),
            show="headings",
            height=15,
        )
        self.tree.grid(row=1, column=0, sticky="nsew", pady=(10, 0))

        for col, text in [
            ("id", "ID"),
            ("name", "Name"),
            ("email", "Email"),
            ("level", "Level"),
            ("active", "Active"),
        ]:
            self.tree.heading(col, text=text)

        self.load_data()

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        try:
            for r in self.repo.list():
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        r.referee_id,
                        r.full_name,
                        r.email,
                        r.level,
                        "yes" if r.active else "no",
                    ),
                )
        except DbError as e:
            messagebox.showerror("DB error", str(e))

    def create_referee(self):
        dlg = RefereeCreateDialog(self)
        self.wait_window(dlg)

        if dlg.result is None:
            return

        try:
            self.repo.insert(dlg.result)
            self.load_data()
        except DbError as e:
            messagebox.showerror("DB error", str(e))
