from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from src.db_mysql import DbError
from src.models.player import Player
from src.models.team import Team
from src.repositories.player_repository import PlayerRepository
from src.repositories.team_repository import TeamRepository
from src.ui.dialogs.player_dialog import PlayerDialog


POSITIONS = ("GK", "DEF", "MID", "ATT")


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
        cols = ("id", "team_id", "first", "last", "birth", "pos")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=18)
        self.tree.grid(row=2, column=0, sticky="nsew", pady=(10, 0))

        self.tree.heading("id", text="ID")
        self.tree.heading("team_id", text="Team ID")
        self.tree.heading("first", text="Jméno")
        self.tree.heading("last", text="Příjmení")
        self.tree.heading("birth", text="Narození")
        self.tree.heading("pos", text="Pozice")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("team_id", width=80, anchor="center")
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
        """
        Returns:
          - None if "All teams" is selected
          - team_id for a concrete team selection
        """
        idx = self.team_cb.current()
        if idx is None or idx < 0:
            return None

        # Index 0 is "All teams"
        if idx == 0:
            return None

        real_idx = idx - 1
        if real_idx < 0 or real_idx >= len(self.teams):
            return None

        return int(self.teams[real_idx].team_id)

    def load_teams(self):
        try:
            self.teams = self.team_repo.list(include_deleted=False)

            labels = ["All teams"]
            labels += [f"{t.class_name} - {t.name} (ID {t.team_id})" for t in self.teams]

            self.team_cb["values"] = labels

            # Default to "All teams" so imported players are visible immediately
            self.team_cb.current(0)
            self.load_players()

        except DbError as e:
            messagebox.showerror("DB ERROR", str(e))

    def load_players(self):
        team_id = self._get_selected_team_id()

        try:
            self._clear()

            # If team_id is None => show all players
            if team_id is None:
                players = self.player_repo.list_all()
            else:
                players = self.player_repo.list_by_team(team_id)

            for p in players:
                self.tree.insert(
                    "",
                    "end",
                    values=(p.player_id, p.team_id, p.first_name, p.last_name, str(p.birth_date), p.position),
                )

        except DbError as e:
            messagebox.showerror("DB ERROR", str(e))

    def add_new(self):
        team_id = self._get_selected_team_id()
        if team_id is None:
            messagebox.showwarning("Pozor", "Vyber konkrétní tým (ne 'All teams').")
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
            messagebox.showwarning("Pozor", "Vyber konkrétní tým (ne 'All teams').")
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

