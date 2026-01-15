from tkinter import ttk

def show_placeholder(container: ttk.Frame, title: str):
    frame = ttk.Frame(container, padding=10)
    frame.grid(row=0, column=0, sticky="nsew")
    ttk.Label(frame, text=title, font=("Arial", 20, "bold")).pack(anchor="w")
    ttk.Label(frame, text="Tady bude další obrazovka v dalším kroku.").pack(anchor="w", pady=(6, 0))


def show_page(container: ttk.Frame, app, key: str, on_test_db):
    if key == "Home":
        from src.ui.screens.home_page import HomePage
        page = HomePage(container, on_test_db=on_test_db)
        page.grid(row=0, column=0, sticky="nsew")
        return

    if key == "Tournaments":
        from src.ui.screens.tournaments_screen import TournamentsScreen
        page = TournamentsScreen(container, app)
        page.grid(row=0, column=0, sticky="nsew")
        return

    if key == "Teams":
        from src.ui.screens.teams_screen import TeamsScreen
        page = TeamsScreen(container, app)
        page.grid(row=0, column=0, sticky="nsew")
        return

    if key == "Players":
        from src.ui.screens.players_screen import PlayersScreen
        page = PlayersScreen(container, app)
        page.grid(row=0, column=0, sticky="nsew")
        return

    if key == "Matches":
        from src.ui.screens.matches_screen import MatchesScreen
        page = MatchesScreen(container, app)
        page.grid(row=0, column=0, sticky="nsew")
        return

    if key == "Referees":
        from src.ui.screens.referees_screen import RefereesScreen
        page = RefereesScreen(container, app)
        page.grid(row=0, column=0, sticky="nsew")
        return

    if key == "Reports":  # example reuse
        from src.ui.screens.match_events_screen import MatchEventsScreen
        page = MatchEventsScreen(container, app)
        page.grid(row=0, column=0, sticky="nsew")
        return

    if key == "Import":
        from src.ui.screens.import_screen import ImportScreen
        page = ImportScreen(container, app)
        page.grid(row=0, column=0, sticky="nsew")
        return

    show_placeholder(container, key)
