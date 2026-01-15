from __future__ import annotations

import csv
from datetime import date

from src.db_mysql import ValidationError
from src.models.team import Team
from src.models.player import Player
from src.repositories.team_repository import TeamRepository
from src.repositories.player_repository import PlayerRepository


class ImportService:
    def __init__(self, team_repo: TeamRepository, player_repo: PlayerRepository):
        self.team_repo = team_repo
        self.player_repo = player_repo

    def import_teams_csv(self, path: str) -> int:
        """
        Imports teams from CSV.
        Expected columns: name, class_name, rating
        """
        count = 0
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row.get("name") or not row.get("class_name"):
                    raise ValidationError("Missing required team fields")

                team = Team(
                    team_id=None,
                    name=row["name"].strip(),
                    class_name=row["class_name"].strip(),
                    rating=float(row["rating"]),
                    is_deleted=False,
                )
                self.team_repo.insert(team)
                count += 1
        return count

    def import_players_csv(self, path: str) -> int:
        """
        Imports players from CSV.
        Expected columns: team_id, first_name, last_name, birth_date, position
        """
        count = 0
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                player = Player(
                    player_id=None,
                    team_id=int(row["team_id"]),
                    first_name=row["first_name"].strip(),
                    last_name=row["last_name"].strip(),
                    birth_date=date.fromisoformat(row["birth_date"]),
                    position=row["position"],
                )
                self.player_repo.insert(player)
                count += 1
        return count
