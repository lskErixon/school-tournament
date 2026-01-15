from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from src.models.player import Player

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
        ttk.Entry(root, textvariable=self.var_first, width=38).grid(row=0, column=1)

        ttk.Label(root, text="Příjmení").grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(root, textvariable=self.var_last, width=38).grid(row=1, column=1, pady=(6, 0))

        ttk.Label(root, text="Datum narození (YYYY-MM-DD)").grid(row=2, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(root, textvariable=self.var_birth, width=38).grid(row=2, column=1, pady=(6, 0))

        ttk.Label(root, text="Pozice").grid(row=3, column=0, sticky="w", pady=(6, 0))
        ttk.Combobox(
            root,
            textvariable=self.var_pos,
            values=POSITIONS,
            state="readonly",
            width=36,
        ).grid(row=3, column=1, pady=(6, 0))

        btns = ttk.Frame(root)
        btns.grid(row=4, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(btns, text="Zrušit", command=self._cancel).pack(side="right")
        ttk.Button(btns, text="Uložit", command=self._save).pack(side="right", padx=(0, 8))

        self.bind("<Escape>", lambda _e: self._cancel())
        self.bind("<Return>", lambda _e: self._save())

    def _cancel(self):
        self.result = None
        self.destroy()

    def _save(self):
        try:
            birth_date = date.fromisoformat(self.var_birth.get().strip())
        except Exception:
            messagebox.showerror("Chyba", "Datum narození musí být YYYY-MM-DD")
            return

        self.result = Player(
            player_id=None,
            team_id=self.team_id,
            first_name=self.var_first.get().strip(),
            last_name=self.var_last.get().strip(),
            birth_date=birth_date,
            position=self.var_pos.get(),
        )
        self.destroy()
