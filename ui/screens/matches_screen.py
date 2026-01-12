from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from src.db_mysql import DbError, ValidationError
from models.match import Match
from models.tournament import Tournament
from models.team import Team
from models.referee import Referee

from repositories.match_repository import MatchRepository
from repositories.tournament_repository import TournamentRepository
from repositories.team_repository import TeamRepository
from repositories.referee_repository import RefereeRepository

STATUSES = ("scheduled", "live", "finished", "cancelled")

class MatchCreateDialog(tk.Toplevel):
    def __init__(self, parent, title: str, tournaments: list[Tournament], teams: list[Team], referees: list[Referee]):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result: tuple[Match, list[int]] | None = None  # (Match, referee_ids)

        self.tournaments = tournaments
        self.teams = teams
        self.referees = referees

        self.transient(parent)
        self.grab_set()

        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)

        # --- Tournament ---
        ttk.Label(root, text="Turnaj").grid(row=0, column=0, sticky="w")
        self.var_tournament = tk.StringVar(value="")
        self.cb_tournament = ttk.Combobox(root, textvariable=self.var_tournament, state="readonly", width=42)
        self.cb_tournament.grid(row=0, column=1, sticky="ew")

        # --- Teams ---
        ttk.Label(root, text="Home team").grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.var_home = tk.StringVar(value="")
        self.cb_home = ttk.Combobox(root, textvariable=self.var_home, state="readonly", width=42)
        self.cb_home.grid(row=1, column=1, sticky="ew", pady=(6, 0))

        ttk.Label(root, text="Away team").grid(row=2, column=0, sticky="w", pady=(6, 0))
        self.var_away = tk.StringVar(value="")
        self.cb_away = ttk.Combobox(root, textvariable=self.var_away, state="readonly", width=42)
        self.cb_away.grid(row=2, column=1, sticky="ew", pady=(6, 0))

        # --- Start time ---
        ttk.Label(root, text="Start time (YYYY-MM-DD HH:MM)").grid(row=3, column=0, sticky="w", pady=(6, 0))
        self.var_start = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d %H:%M"))
        ttk.Entry(root, textvariable=self.var_start, width=45).grid(row=3, column=1, sticky="ew", pady=(6, 0))

        # --- Status / overtime ---
        ttk.Label(root, text="Status").grid(row=4, column=0, sticky="w", pady=(6, 0))
        self.var_status = tk.StringVar(value="scheduled")
        cb_status = ttk.Combobox(root, textvariable=self.var_status, values=STATUSES, state="readonly", width=42)
        cb_status.grid(row=4, column=1, sticky="ew", pady=(6, 0))

        self.var_overtime = tk.IntVar(value=0)
        ttk.Checkbutton(root, text="Overtime", variable=self.var_overtime).grid(row=5, column=1, sticky="w", pady=(6, 0))

        # --- Referees listbox (M:N) ---
        ttk.Label(root, text="Rozhodčí (vyber 1+)",).grid(row=6, column=0, sticky="nw", pady=(10, 0))
        ref_frame = ttk.Frame(root)
        ref_frame.grid(row=6, column=1, sticky="ew", pady=(10, 0))

        self.lb_refs = tk.Listbox(ref_frame, selectmode="extended", height=6, exportselection=False)
        self.lb_refs.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(ref_frame, orient="vertical", command=self.lb_refs.yview)
        sb.pack(side="right", fill="y")
        self.lb_refs.configure(yscrollcommand=sb.set)

        # buttons
        btns = ttk.Frame(root)
        btns.grid(row=7, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(btns, text="Zrušit", command=self._cancel).pack(side="right")
        ttk.Button(btns, text="Vytvořit", command=self._save).pack(side="right", padx=(0, 8))

        root.columnconfigure(1, weight=1)

        self.bind("<Escape>", lambda _e: self._cancel())
        self.bind("<Return>", lambda _e: self._save())

        self._fill_data()
        self._center(parent)

    def _fill_data(self):
        t_labels = [f"{t.name} (ID {t.tournament_id})" for t in self.tournaments]
        self.cb_tournament["values"] = t_labels
        if t_labels:
            self.cb_tournament.current(0)

        team_labels = [f"{t.class_name} - {t.name} (ID {t.team_id})" for t in self.teams]
        self.cb_home["values"] = team_labels
        self.cb_away["values"] = team_labels
        if team_labels:
            self.cb_home.current(0)
            if len(team_labels) > 1:
                self.cb_away.current(1)
            else:
                self.cb_away.current(0)

        self.lb_refs.delete(0, tk.END)
        for r in self.referees:
            self.lb_refs.insert(tk.END, f"{r.full_name} ({r.level}) (ID {r.referee_id})")

    def _center(self, parent):
        self.update_idletasks()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{px + (pw - w)//2}+{py + (ph - h)//2}")

    def _cancel(self):
        self.result = None
        self.destroy()

    def _get_selected_id(self, cb: ttk.Combobox, items, id_attr: str) -> int:
        idx = cb.current()
        if idx is None or idx < 0 or idx >= len(items):
            raise ValidationError("Vyber hodnotu v comboboxu.")
        return int(getattr(items[idx], id_attr))

    def _parse_dt(self, value: str) -> datetime:
        try:
            return datetime.strptime(value.strip(), "%Y-%m-%d %H:%M")
        except Exception:
            raise ValidationError("Start time: špatný formát. Použij YYYY-MM-DD HH:MM")

    def _save(self):
        try:
            tournament_id = self._get_selected_id(self.cb_tournament, self.tournaments, "tournament_id")
            home_team_id = self._get_selected_id(self.cb_home, self.teams, "team_id")
            away_team_id = self._get_selected_id(self.cb_away, self.teams, "team_id")

            if home_team_id == away_team_id:
                raise ValidationError("Home a Away tým nesmí být stejný.")

            start_time = self._parse_dt(self.var_start.get())
            status = self.var_status.get().strip()
            if status not in STATUSES:
                raise ValidationError("Neplatný status.")

            is_overtime = bool(self.var_overtime.get())

            selected = list(self.lb_refs.curselection())
            if not selected:
                raise ValidationError("Vyber aspoň 1 rozhodčího.")

            referee_ids = [int(self.referees[i].referee_id) for i in selected]

            match = Match(
                match_id=None,
                tournament_id=tournament_id,
                home_team_id=home_team_id,
                away_team_id=away_team_id,
                start_time=start_time,
                status=status,
                is_overtime=is_overtime,
            )

            self.result = (match, referee_ids)
            self.destroy()

        except ValidationError as e:
            messagebox.showerror("Chyba", str(e))


class MatchesScreen(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=10)
        self.app = app

        self.match_repo = MatchRepository(app.db)
        self.tournament_repo = TournamentRepository(app.db)
        self.team_repo = TeamRepository(app.db)
        self.ref_repo = RefereeRepository(app.db)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Zápasy", font=("Arial", 20, "bold")).grid(row=0, column=0, sticky="w")

        toolbar = ttk.Frame(header)
        toolbar.grid(row=0, column=1, sticky="e")
        ttk.Button(toolbar, text="Refresh", command=self.load_data).pack(side="right")
        ttk.Button(toolbar, text="Vytvořit zápas", command=self.create_match).pack(side="right", padx=(0, 8))

        cols = ("id", "tournament", "home", "away", "start", "status", "ot")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=18)
        self.tree.grid(row=1, column=0, sticky="nsew", pady=(10, 0))

        self.tree.heading("id", text="ID")
        self.tree.heading("tournament", text="Turnaj")
        self.tree.heading("home", text="Home")
        self.tree.heading("away", text="Away")
        self.tree.heading("start", text="Start")
        self.tree.heading("status", text="Status")
        self.tree.heading("ot", text="OT")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("tournament", width=220, anchor="w")
        self.tree.column("home", width=200, anchor="w")
        self.tree.column("away", width=200, anchor="w")
        self.tree.column("start", width=150, anchor="center")
        self.tree.column("status", width=90, anchor="center")
        self.tree.column("ot", width=60, anchor="center")

        sb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        sb.grid(row=1, column=1, sticky="ns", pady=(10, 0))
        self.tree.configure(yscrollcommand=sb.set)

        self.load_data()

    def _clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def load_data(self):
        try:
            self._clear()
            rows = self.match_repo.list_with_names()
            for r in rows:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        r["match_id"],
                        r["tournament_name"],
                        r["home_team_name"],
                        r["away_team_name"],
                        r["start_time"],
                        r["status"],
                        "yes" if r["is_overtime"] else "no",
                    ),
                )
        except DbError as e:
            messagebox.showerror("DB ERROR", str(e))

    def create_match(self):
        try:
            tournaments = self.tournament_repo.list()
            teams = self.team_repo.list(include_deleted=False)
            referees = self.ref_repo.list(active_only=True)
        except DbError as e:
            messagebox.showerror("DB ERROR", str(e))
            return

        if not tournaments:
            messagebox.showwarning("Pozor", "Nejdřív vytvoř turnaj (Turnaje).")
            return
        if len(teams) < 2:
            messagebox.showwarning("Pozor", "Nejdřív vytvoř aspoň 2 týmy (Týmy).")
            return
        if not referees:
            messagebox.showwarning("Pozor", "Nejdřív vytvoř aspoň 1 rozhodčího (Rozhodčí).")
            return

        dlg = MatchCreateDialog(self, "Vytvořit zápas", tournaments, teams, referees)
        self.wait_window(dlg)
        if dlg.result is None:
            return

        match, referee_ids = dlg.result

        try:
            new_id = self.match_repo.create_match_with_referees(match, referee_ids)
            self.load_data()
            messagebox.showinfo("OK", f"Zápas vytvořen (ID: {new_id}).")
        except DbError as e:
            messagebox.showerror("DB ERROR", str(e))
