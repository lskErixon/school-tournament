from tkinter import ttk

class Sidebar(ttk.Frame):
    def __init__(self, parent, on_navigate, on_test_db):
        super().__init__(parent, padding=10)

        ttk.Label(self, text="Menu", font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))

        pages = [
            ("Home", "Home"),
            ("Turnaje", "Tournaments"),
            ("Týmy", "Teams"),
            ("Hráči", "Players"),
            ("Referees", "Referees"),
            ("Zápasy", "Matches"),
            ("Import", "Import"),
            ("Reporty", "Reports"),
        ]

        for text, key in pages:
            ttk.Button(self, text=text, command=lambda k=key: on_navigate(k)).pack(fill="x", pady=4)

        ttk.Separator(self).pack(fill="x", pady=12)
        ttk.Button(self, text="Test DB connection", command=on_test_db).pack(fill="x")
