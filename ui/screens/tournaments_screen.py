from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from src.db_mysql import DbError, NotFoundError, ValidationError
from models.tournament import Tournament
from repositories.tournament_repository import TournamentRepository

class TournamentDialog(tk.Toplevel):
    def __init__(self, parent, title: str, initial: Tournament | None):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result: Tournament | None = None

        self.transient(parent)
        self.grab_set()

        pad = 10
        root = ttk.Frame(self, padding=pad)
        root.pack(fill="both", expand=True)

        # Vars
        self.var_name = tk.StringVar(value=initial.name if initial else "")
        self.var_start = tk.StringVar(value=str(initial.start_date) if initial else "")
        self.var_end = tk.StringVar(value=str(initial.end_date) if (initial and initial.end_date) else "")
        self.var_active = tk.IntVar(value=1 if (initial.is_active if initial else True) else 0)

        # Form
        ttk.Label(root, text="Název").grid(row=0, column=0, sticky="w")
        ttk.Entry(root, textvariable=self.var_name, width=38).grid(row=0, column=1, sticky="ew")

        ttk.Label(root, text="Start date (YYYY-MM-DD)").grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(root, textvariable=self.var_start, width=38).grid(row=1, column=1, sticky="ew", pady=(6, 0))

        ttk.Label(root, text="End date (YYYY-MM-DD) (optional)").grid(row=2, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(root, textvariable=self.var_end, width=38).grid(row=2, column=1, sticky="ew", pady=(6, 0))

        ttk.Checkbutton(root, text="Aktivní", variable=self.var_active).grid(row=3, column=1, sticky="w", pady=(8, 0))

        # Buttons
        btns = ttk.Frame(root)
        btns.grid(row=4, column=0, columnspan=2, sticky="e", pady=(12, 0))

        ttk.Button(btns, text="Zrušit", command=self._cancel).pack(side="right")
        ttk.Button(btns, text="Uložit", command=self._save).pack(side="right", padx=(0, 8))

        root.columnconfigure(1, weight=1)

        self.bind("<Escape>", lambda _e: self._cancel())
        self.bind("<Return>", lambda _e: self._save())

        self._center(parent)

    def _center(self, parent):
        self.update_idletasks()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()

        w = self.winfo_width()
        h = self.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")

    def _cancel(self):
        self.result = None
        self.destroy()

    @staticmethod
    def _parse_date(value: str, field_name: str) -> date:
        try:
            return date.fromisoformat(value.strip())
        except Exception:
            raise ValidationError(f"{field_name}: špatný formát. Použij YYYY-MM-DD")

    def _save(self):
        name = self.var_name.get().strip()
        if not name:
            messagebox.showerror("Chyba", "Název nesmí být prázdný.")
            return

        try:
            start_date = self._parse_date(self.var_start.get(), "Start date")
            end_raw = self.var_end.get().strip()
            end_date = self._parse_date(end_raw, "End date") if end_raw else None

            if end_date is not None and end_date < start_date:
                raise ValidationError("End date nesmí být menší než Start date.")

            is_active = bool(self.var_active.get())

            self.result = Tournament(
                tournament_id=None,
                name=name,
                start_date=start_date,
                end_date=end_date,
                is_active=is_active,
            )
            self.destroy()

        except ValidationError as e:
            messagebox.showerror("Chyba", str(e))


class TournamentsScreen(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=10)
        self.app = app
        self.repo = TournamentRepository(app.db)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        ttk.Label(self, text="Turnaje", font=("Arial", 20, "bold")).grid(row=0, column=0, sticky="w")

        toolbar = ttk.Frame(self)
        toolbar.grid(row=0, column=0, sticky="e")

        ttk.Button(toolbar, text="Refresh", command=self.load_data).pack(side="right")
        ttk.Button(toolbar, text="Smazat", command=self.delete_selected).pack(side="right", padx=(0, 8))
        ttk.Button(toolbar, text="Upravit", command=self.edit_selected).pack(side="right", padx=(0, 8))
        ttk.Button(toolbar, text="Přidat", command=self.add_new).pack(side="right", padx=(0, 8))

        # Table
        cols = ("id", "name", "start_date", "end_date", "active")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=18)
        self.tree.grid(row=1, column=0, sticky="nsew", pady=(10, 0))

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Název")
        self.tree.heading("start_date", text="Start")
        self.tree.heading("end_date", text="End")
        self.tree.heading("active", text="Aktivní")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("name", width=320, anchor="w")
        self.tree.column("start_date", width=120, anchor="center")
        self.tree.column("end_date", width=120, anchor="center")
        self.tree.column("active", width=80, anchor="center")

        # Scrollbar
        sb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        sb.grid(row=1, column=1, sticky="ns", pady=(10, 0))
        self.tree.configure(yscrollcommand=sb.set)

        # Double click = edit
        self.tree.bind("<Double-1>", lambda _e: self.edit_selected())

        self.load_data()

    def _clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def load_data(self):
        try:
            self._clear()
            tournaments = self.repo.list()
            for t in tournaments:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        t.tournament_id,
                        t.name,
                        str(t.start_date),
                        "" if t.end_date is None else str(t.end_date),
                        "yes" if t.is_active else "no",
                    ),
                )
        except DbError as e:
            messagebox.showerror("DB ERROR", str(e))

    def _get_selected_id(self) -> int | None:
        sel = self.tree.selection()
        if not sel:
            return None
        values = self.tree.item(sel[0], "values")
        return int(values[0])

    def add_new(self):
        dlg = TournamentDialog(self, "Přidat turnaj", None)
        self.wait_window(dlg)
        if dlg.result is None:
            return

        try:
            new_id = self.repo.insert(dlg.result)
            self.load_data()
            messagebox.showinfo("OK", f"Turnaj byl vytvořen (ID: {new_id}).")
        except DbError as e:
            messagebox.showerror("DB ERROR", str(e))

    def edit_selected(self):
        tid = self._get_selected_id()
        if tid is None:
            messagebox.showwarning("Pozor", "Vyber turnaj v tabulce.")
            return

        try:
            current = self.repo.get_by_id(tid)
        except DbError as e:
            messagebox.showerror("DB ERROR", str(e))
            return

        dlg = TournamentDialog(self, "Upravit turnaj", current)
        self.wait_window(dlg)
        if dlg.result is None:
            return

        edited = Tournament(
            tournament_id=tid,
            name=dlg.result.name,
            start_date=dlg.result.start_date,
            end_date=dlg.result.end_date,
            is_active=dlg.result.is_active,
        )

        try:
            self.repo.update(edited)
            self.load_data()
            messagebox.showinfo("OK", "Turnaj byl upraven.")
        except DbError as e:
            messagebox.showerror("DB ERROR", str(e))

    def delete_selected(self):
        tid = self._get_selected_id()
        if tid is None:
            messagebox.showwarning("Pozor", "Vyber turnaj v tabulce.")
            return

        if not messagebox.askyesno("Potvrzení", f"Opravdu smazat turnaj ID {tid}?"):
            return

        try:
            self.repo.delete(tid)
            self.load_data()
            messagebox.showinfo("OK", "Turnaj byl smazán.")
        except DbError as e:
            messagebox.showerror("DB ERROR", str(e))
