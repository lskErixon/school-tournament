from __future__ import annotations

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from src.services.import_service import ImportService
from src.repositories.team_repository import TeamRepository
from src.repositories.player_repository import PlayerRepository
from src.db_mysql import DbError


class ImportScreen(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=10)
        self.app = app

        self.service = ImportService(
            TeamRepository(app.db),
            PlayerRepository(app.db),
        )

        ttk.Label(self, text="Import data", font=("Arial", 20, "bold")).pack(anchor="w")

        box = ttk.LabelFrame(self, text="CSV Import", padding=10)
        box.pack(fill="x", pady=10)

        self.var_type = tk.StringVar(value="teams")

        ttk.Radiobutton(box, text="Teams", variable=self.var_type, value="teams").pack(anchor="w")
        ttk.Radiobutton(box, text="Players", variable=self.var_type, value="players").pack(anchor="w")

        ttk.Button(box, text="Select CSV file", command=self.select_file).pack(pady=8)

    def select_file(self):
        path = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv")],
        )
        if not path:
            return

        try:
            if self.var_type.get() == "teams":
                count = self.service.import_teams_csv(path)
                messagebox.showinfo("Import finished", f"Imported {count} teams")
            else:
                count = self.service.import_players_csv(path)
                messagebox.showinfo("Import finished", f"Imported {count} players")

        except (DbError, ValueError) as e:
            messagebox.showerror("Import error", str(e))
