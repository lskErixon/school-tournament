from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from src.db_mysql import DbError, NotFoundError, ValidationError
from models.team import Team
from repositories.team_repository import TeamRepository


class TeamDialog(tk.Toplevel):
    def __init__(self, parent, title: str, initial: Team | None):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result: Team | None = None

        self.transient(parent)
        self.grab_set()

        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)

        self.var_name = tk.StringVar(value=initial.name if initial else "")
        self.var_class = tk.StringVar(value=initial.class_name if initial else "")
        self.var_rating = tk.StringVar(value=str(initial.rating) if initial else "1000.0")

        ttk.Label(root, text="Název").grid(row=0, column=0, sticky="w")
        ttk.Entry(root, textvariable=self.var_name, width=38).grid(row=0, column=1, sticky="ew")

        ttk.Label(root, text="Třída (např. 4.A)").grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(root, textvariable=self.var_class, width=38).grid(row=1, column=1, sticky="ew", pady=(6, 0))

        ttk.Label(root, text="Rating (float)").grid(row=2, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(root, textvariable=self.var_rating, width=38).grid(row=2, column=1, sticky="ew", pady=(6, 0))

        btns = ttk.Frame(root)
        btns.grid(row=3, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(btns, text="Zrušit", command=self._cancel).pack(side="right")
        ttk.Button(btns, text="Uložit", command=self._save).pack(side="right", padx=(0, 8))

        root.columnconfigure(1, weight=1)
        self.bind("<Escape>", lambda _e: self._cancel())
        self.bind("<Return>", lambda _e: self._save())

        self._center(parent)

    def _center(self, parent):
        self.update_idletasks()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{px + (pw - w)//2}+{py + (ph - h)//2}")

    def _cancel(self):
        self.result = None
        self.destroy()

    def _save(self):
        name = self.var_name.get().strip()
        class_name = self.var_class.get().strip()
        rating_raw = self.var_rating.get().strip()

        if not name:
            messagebox.showerror("Chyba", "Název nesmí být prázdný.")
            return
        if not class_name:
            messagebox.showerror("Chyba", "Třída nesmí být prázdná.")
            return

        try:
            rating = float(rating_raw)
        except Exception:
            messagebox.showerror("Chyba", "Rating musí být číslo (float).")
            return

        self.result = Team(
            team_id=None,
            name=name,
            class_name=class_name,
            rating=rating,
            is_deleted=False,
        )
        self.destroy()


class TeamsScreen(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=10)
        self.app = app
        self.repo = TeamRepository(app.db)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Týmy", font=("Arial", 20, "bold")).grid(row=0, column=0, sticky="w")

        toolbar = ttk.Frame(header)
        toolbar.grid(row=0, column=1, sticky="e")

        ttk.Button(toolbar, text="Refresh", command=self.load_data).pack(side="right")
        ttk.Button(toolbar, text="Restore", command=self.restore_selected).pack(side="right", padx=(0, 8))
        ttk.Button(toolbar, text="Soft delete", command=self.soft_delete_selected).pack(side="right", padx=(0, 8))
        ttk.Button(toolbar, text="Upravit", command=self.edit_selected).pack(side="right", padx=(0, 8))
        ttk.Button(toolbar, text="Přidat", command=self.add_new).pack(side="right", padx=(0, 8))

        # filter row
        filters = ttk.Frame(self)
        filters.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        self.var_include_deleted = tk.IntVar(value=0)
        ttk.Checkbutton(
            filters,
            text="Zobrazit smazané (is_deleted=1)",
            variable=self.var_include_deleted,
            command=self.load_data,
        ).pack(anchor="w")

        # table
        cols = ("id", "name", "class_name", "rating", "deleted")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=18)
        self.tree.grid(row=2, column=0, sticky="nsew", pady=(10, 0))

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Název")
        self.tree.heading("class_name", text="Třída")
        self.tree.heading("rating", text="Rating")
        self.tree.heading("deleted", text="Smazaný")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("name", width=280, anchor="w")
        self.tree.column("class_name", width=100, anchor="center")
        self.tree.column("rating", width=90, anchor="center")
        self.tree.column("deleted", width=90, anchor="center")

        sb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        sb.grid(row=2, column=1, sticky="ns", pady=(10, 0))
        self.tree.configure(yscrollcommand=sb.set)

        self.tree.bind("<Double-1>", lambda _e: self.edit_selected())

        self.load_data()

    def _clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def _get_selected_id(self) -> int | None:
        sel = self.tree.selection()
        if not sel:
            return None
        return int(self.tree.item(sel[0], "values")[0])

    def load_data(self):
        try:
            self._clear()
            include_deleted = bool(self.var_include_deleted.get())
            teams = self.repo.list(include_deleted=include_deleted)
            for t in teams:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        t.team_id,
                        t.name,
                        t.class_name,
                        f"{t.rating:.2f}",
                        "yes" if t.is_deleted else "no",
                    ),
                )
        except DbError as e:
            messagebox.showerror("DB ERROR", str(e))

    def add_new(self):
        dlg = TeamDialog(self, "Přidat tým", None)
        self.wait_window(dlg)
        if dlg.result is None:
            return

        try:
            new_id = self.repo.insert(dlg.result)
            self.load_data()
            messagebox.showinfo("OK", f"Tým vytvořen (ID: {new_id}).")
        except DbError as e:
            messagebox.showerror("DB ERROR", str(e))

    def edit_selected(self):
        team_id = self._get_selected_id()
        if team_id is None:
            messagebox.showwarning("Pozor", "Vyber tým v tabulce.")
            return

        try:
            current = self.repo.get_by_id(team_id, include_deleted=True)
        except DbError as e:
            messagebox.showerror("DB ERROR", str(e))
            return

        dlg = TeamDialog(self, "Upravit tým", current)
        self.wait_window(dlg)
        if dlg.result is None:
            return

        edited = Team(
            team_id=team_id,
            name=dlg.result.name,
            class_name=dlg.result.class_name,
            rating=dlg.result.rating,
            is_deleted=current.is_deleted,
        )

        try:
            self.repo.update(edited)
            self.load_data()
            messagebox.showinfo("OK", "Tým upraven.")
        except DbError as e:
            messagebox.showerror("DB ERROR", str(e))

    def soft_delete_selected(self):
        team_id = self._get_selected_id()
        if team_id is None:
            messagebox.showwarning("Pozor", "Vyber tým v tabulce.")
            return

        if not messagebox.askyesno("Potvrzení", f"Opravdu soft-delete tým ID {team_id}?"):
            return

        try:
            self.repo.soft_delete(team_id)
            self.load_data()
            messagebox.showinfo("OK", "Tým byl označen jako smazaný (is_deleted=1).")
        except DbError as e:
            messagebox.showerror("DB ERROR", str(e))

    def restore_selected(self):
        team_id = self._get_selected_id()
        if team_id is None:
            messagebox.showwarning("Pozor", "Vyber tým v tabulce.")
            return

        try:
            self.repo.restore(team_id)
            self.load_data()
            messagebox.showinfo("OK", "Tým byl obnoven (is_deleted=0).")
        except DbError as e:
            messagebox.showerror("DB ERROR", str(e))
