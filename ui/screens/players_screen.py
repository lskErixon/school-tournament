from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from src.db_mysql import DbError, NotFoundError, ValidationError
from models.player import Player
from models.team import Team
from repositories.player_repository import PlayerRepository
from repositories.team_repository import TeamRepository


POSITIONS = ("GK", "DEF", "MID", "ATT")


class PlayerDialog(tk.Toplevel):
    def __init__(self, parent, title: str, team_id: int, initial: Player | None):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result: Player | None = None

        self.transient(parent)
        self.grab_set()

        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)

        self.team_id = team_id

        self.var_first = tk.StringVar(value=initial.first_name if initial else "")
        self.var_last = tk.StringVar(value=initial.last_name if initial else "")
        self.var_birth = tk.StringVar(value=str(initial.birth_date) if initial else "")
        self.var_pos = tk.StringVar(value=initial.position if initial else POSITIONS[0])

        ttk.Label(root, text="Jméno").grid(row=0, column=0, sticky="w")
        ttk.Entry(root, textvariable=self.var_first, width=38).grid(row=0, column=1, sticky="ew")

        ttk.Label(root, text="Příjmení").grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(root, textvariable=self.var_last, width=38).grid(row=1, column=1, sticky="ew", pady=(6, 0))

        ttk.Label(root, text="Datum narození (YYYY-MM-DD)").grid(row=2, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(root, textvariable=self.var_birth, width=38).grid(row=2, column=1, sticky="ew", pady=(6, 0))

        ttk.Label(root, text="Pozice").grid(row=3, column=0, sticky="w", pady=(6, 0))
        cb = ttk.Combobox(root, textvariable=self.var_pos, values=POSITIONS, state="readonly", width=36)
        cb.grid(row=3, column=1, sticky="ew", pady=(6, 0))

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
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{px + (pw - w)//2}+{py + (ph - h)//2}")

    def _cancel(self):
        self.result = None
        self.destroy()

    @staticmethod
    def _parse_date(value: str) -> date:
        try:
            return date.fromisoformat(value.strip())
        except Exception:
            raise ValidationError("Datum narození: špatný formát. Použij YYYY-MM-DD")

    def _save(self):
        first_name = self.var_first.get().strip()
        last_name = self.var_last.get().strip()
        birth_raw = self.var_birth.get().strip()
        pos = self.var_pos.get().strip()

        if not first_name or not last_name:
            messagebox.showerror("Chyba", "Jméno i příjmení musí být vyplněné.")
            return

        try:
            birth_date = self._parse_date(birth_raw)
            if pos not in POSITIONS:
                raise ValidationError("Pozice musí být jedna z: GK/DEF/MID/ATT")

            self.result = Player(
                player_id=None,
                team_id=self.team_id,
                first_name=first_name,
                last_name=last_name,
                birth_date=birth_date,
                position=pos,
            )
            self.destroy()

        except ValidationError as e:
            messagebox.showerror("Chyba", str(e))


class PlayersScreen(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=10)
        self.app = app
        self.team_repo = TeamRepository(app.db)
        self.player_repo = PlayerRepository(app.db)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Hráči", font=("Arial", 20, "bold")).grid(row=0, column=0, sticky="w")

        toolbar = ttk.Frame(header)
        toolbar.grid(row=0, column=1, sticky="e")

        ttk.Button(toolbar, text="Refresh", command=self.load_players).pack(side="right")
        ttk.Button(toolbar, text="Smazat", command=self.delete_selected).pack(side="right", padx=(0, 8))
        ttk.Button(toolbar, text="Upravit", command=self.edit_selected).pack(side="right", padx=(0, 8))
        ttk.Button(toolbar, text="Přidat", command=self.add_new).pack(side="right", padx=(0, 8))

        # Team selector
        top = ttk.Frame(self)
        top.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        ttk.Label(top, text="Tým:").pack(side="left")

        self.teams: list[Team] = []
        self.team_var = tk.StringVar(value="")
        self.team_cb = ttk.Combobox(top, textvariable=self.team_var, state="readonly", width=40)
        self.team_cb.pack(side="left", padx=(8, 0))
        self.team_cb.bind("<<ComboboxSelected>>", lambda _e: self.load_players())

        # Table
        cols = ("id", "first", "last", "birth", "pos")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=18)
        self.tree.grid(row=2, column=0, sticky="nsew", pady=(10, 0))

        self.tree.heading("id", text="ID")
        self.tree.heading("first", text="Jméno")
        self.tree.heading("last", text="Příjmení")
        self.tree.heading("birth", text="Narození")
        self.tree.heading("pos", text="Pozice")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("first", width=180, anchor="w")
        self.tree.column("last", width=200, anchor="w")
        self.tree.column("birth", width=120, anchor="center")
        self.tree.column("pos", width=80, anchor="center")

        sb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        sb.grid(row=2, column=1, sticky="ns", pady=(10, 0))
        self.tree.configure(yscrollcommand=sb.set)

        self.tree.bind("<Double-1>", lambda _e: self.edit_selected())

        self.load_teams()

    def _clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def _get_selected_player_id(self) -> int | None:
        sel = self.tree.selection()
        if not sel:
            return None
        return int(self.tree.item(sel[0], "values")[0])

    def _get_selected_team_id(self) -> int | None:
        idx = self.team_cb.current()
        if idx is None or idx < 0 or idx >= len(self.teams):
            return None
        return int(self.teams[idx].team_id)

    def load_teams(self):
        try:
            self.teams = self.team_repo.list(include_deleted=False)
            labels = [f"{t.class_name} - {t.name} (ID {t.team_id})" for t in self.teams]
            self.team_cb["values"] = labels

            if labels:
                self.team_cb.current(0)
                self.load_players()
            else:
                self._clear()
                messagebox.showwarning("Pozor", "Nejdřív vytvoř aspoň jeden tým (Týmy → Přidat).")

        except DbError as e:
            messagebox.showerror("DB ERROR", str(e))

    def load_players(self):
        team_id = self._get_selected_team_id()
        if team_id is None:
            self._clear()
            return

        try:
            self._clear()
            players = self.player_repo.list_by_team(team_id)
            for p in players:
                self.tree.insert(
                    "",
                    "end",
                    values=(p.player_id, p.first_name, p.last_name, str(p.birth_date), p.position),
                )
        except DbError as e:
            messagebox.showerror("DB ERROR", str(e))

    def add_new(self):
        team_id = self._get_selected_team_id()
        if team_id is None:
            messagebox.showwarning("Pozor", "Vyber tým.")
            return

        dlg = PlayerDialog(self, "Přidat hráče", team_id, None)
        self.wait_window(dlg)
        if dlg.result is None:
            return

        try:
            new_id = self.player_repo.insert(dlg.result)
            self.load_players()
            messagebox.showinfo("OK", f"Hráč vytvořen (ID: {new_id}).")
        except DbError as e:
            messagebox.showerror("DB ERROR", str(e))

    def edit_selected(self):
        team_id = self._get_selected_team_id()
        if team_id is None:
            messagebox.showwarning("Pozor", "Vyber tým.")
            return

        pid = self._get_selected_player_id()
        if pid is None:
            messagebox.showwarning("Pozor", "Vyber hráče v tabulce.")
            return

        try:
            current = self.player_repo.get_by_id(pid)
        except DbError as e:
            messagebox.showerror("DB ERROR", str(e))
            return

        dlg = PlayerDialog(self, "Upravit hráče", team_id, current)
        self.wait_window(dlg)
        if dlg.result is None:
            return

        edited = Player(
            player_id=pid,
            team_id=team_id,
            first_name=dlg.result.first_name,
            last_name=dlg.result.last_name,
            birth_date=dlg.result.birth_date,
            position=dlg.result.position,
        )

        try:
            self.player_repo.update(edited)
            self.load_players()
            messagebox.showinfo("OK", "Hráč upraven.")
        except DbError as e:
            messagebox.showerror("DB ERROR", str(e))

    def delete_selected(self):
        pid = self._get_selected_player_id()
        if pid is None:
            messagebox.showwarning("Pozor", "Vyber hráče v tabulce.")
            return

        if not messagebox.askyesno("Potvrzení", f"Opravdu smazat hráče ID {pid}?"):
            return

        try:
            self.player_repo.delete(pid)
            self.load_players()
            messagebox.showinfo("OK", "Hráč smazán.")
        except DbError as e:
            messagebox.showerror("DB ERROR", str(e))
