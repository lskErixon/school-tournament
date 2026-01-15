from tkinter import ttk, messagebox

from src.db_mysql import DbError
from src.ui.widgets.sidebar import Sidebar
from src.ui.router import show_page


class HomeScreen(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=10)
        self.app = app

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, on_navigate=self.navigate, on_test_db=self.test_db)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.content = ttk.Frame(self, padding=12)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=1)

        self.navigate("Home")

    def _clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    def navigate(self, key: str):
        self._clear_content()
        show_page(self.content, self.app, key, on_test_db=self.test_db)

    def test_db(self):
        try:
            with self.app.db.conn() as cnx, self.app.db.cursor(cnx) as cur:
                cur.execute("SELECT 1 AS ok")
                row = cur.fetchone()
            messagebox.showinfo("DB OK", f"Connected. SELECT 1 -> {row['ok']}")
        except DbError as e:
            messagebox.showerror("DB ERROR", str(e))
