from tkinter import ttk

class HomePage(ttk.Frame):
    def __init__(self, parent, on_test_db):
        super().__init__(parent, padding=10)

        ttk.Label(self, text="School Tournament (D1)", font=("Arial", 22, "bold")).pack(anchor="w")

        ttk.Separator(self).pack(fill="x", pady=18)

        ttk.Label(self, text="Rychlé akce:", font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 8))
        ttk.Button(self, text="Test DB connection", command=on_test_db).pack(anchor="w")

        ttk.Separator(self).pack(fill="x", pady=18)
