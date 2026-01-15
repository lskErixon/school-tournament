from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from src.models.match_event import MatchEvent
from src.repositories.match_event_repository import MatchEventRepository
from src.repositories.match_repository import MatchRepository
from src.db_mysql import DbError


EVENT_TYPES = ("goal", "own_goal", "yellow", "red")


class MatchEventsScreen(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=10)
        self.app = app

        self.match_repo = MatchRepository(app.db)
        self.repo = MatchEventRepository(app.db)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        ttk.Label(self, text="Match events", font=("Arial", 20, "bold")).grid(
            row=0, column=0, sticky="w"
        )

        form = ttk.Frame(self)
        form.grid(row=1, column=0, sticky="ew", pady=10)

        ttk.Label(form, text="Match ID").grid(row=0, column=0)
        self.var_match = tk.StringVar()
        ttk.Entry(form, textvariable=self.var_match, width=8).grid(row=0, column=1)

        ttk.Label(form, text="Team ID").grid(row=0, column=2, padx=(10, 0))
        self.var_team = tk.StringVar()
        ttk.Entry(form, textvariable=self.var_team, width=8).grid(row=0, column=3)

        ttk.Label(form, text="Player ID").grid(row=0, column=4, padx=(10, 0))
        self.var_player = tk.StringVar()
        ttk.Entry(form, textvariable=self.var_player, width=8).grid(row=0, column=5)

        ttk.Label(form, text="Minute").grid(row=0, column=6, padx=(10, 0))
        self.var_minute = tk.StringVar()
        ttk.Entry(form, textvariable=self.var_minute, width=6).grid(row=0, column=7)

        ttk.Label(form, text="Type").grid(row=0, column=8, padx=(10, 0))
        self.var_type = tk.StringVar(value="goal")
        ttk.Combobox(
            form,
            textvariable=self.var_type,
            values=EVENT_TYPES,
            state="readonly",
            width=10,
        ).grid(row=0, column=9)

        ttk.Button(form, text="Add event", command=self.add_event).grid(
            row=0, column=10, padx=(10, 0)
        )

        self.tree = ttk.Treeview(
            self,
            columns=("id", "minute", "type", "team", "player"),
            show="headings",
        )
        self.tree.grid(row=2, column=0, sticky="nsew")

        for col, txt in [
            ("id", "ID"),
            ("minute", "Minute"),
            ("type", "Type"),
            ("team", "Team ID"),
            ("player", "Player ID"),
        ]:
            self.tree.heading(col, text=txt)

    def load_events(self, match_id: int):
        self.tree.delete(*self.tree.get_children())
        try:
            for e in self.repo.list_by_match(match_id):
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        e.event_id,
                        e.minute,
                        e.event_type,
                        e.team_id,
                        e.player_id or "",
                    ),
                )
        except DbError as e:
            messagebox.showerror("DB error", str(e))

    def add_event(self):
        try:
            match_id = int(self.var_match.get())
            team_id = int(self.var_team.get())
            minute = int(self.var_minute.get())
            player_id = self.var_player.get().strip()
            player_id = int(player_id) if player_id else None

            event = MatchEvent(
                event_id=None,
                match_id=match_id,
                player_id=player_id,
                team_id=team_id,
                minute=minute,
                event_type=self.var_type.get(),
                xg=None,
                created_at=None,
            )

            self.repo.insert(event)
            self.load_events(match_id)

        except ValueError:
            messagebox.showerror("Error", "Invalid numeric value")
        except DbError as e:
            messagebox.showerror("DB error", str(e))
