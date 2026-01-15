from typing import List
from src.db_mysql import Db, NotFoundError
from src.models.player import Player


class PlayerRepository:
    def __init__(self, db: Db):
        self.db = db

    def get_by_id(self, player_id: int) -> Player:
        sql = """
        SELECT player_id, team_id, first_name, last_name, birth_date, position
        FROM player
        WHERE player_id=%s
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (player_id,))
            row = cur.fetchone()
            if not row:
                raise NotFoundError(f"Player {player_id} not found")
            return Player(**row)

    def list_all(self) -> List[Player]:
        """
        Returns all players (no team filter).
        """
        sql = """
        SELECT player_id, team_id, first_name, last_name, birth_date, position
        FROM player
        ORDER BY last_name, first_name
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql)
            return [Player(**r) for r in cur.fetchall()]

    def list_by_team(self, team_id: int) -> List[Player]:
        sql = """
        SELECT player_id, team_id, first_name, last_name, birth_date, position
        FROM player
        WHERE team_id=%s
        ORDER BY last_name, first_name
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (team_id,))
            return [Player(**r) for r in cur.fetchall()]

    def insert(self, p: Player) -> int:
        sql = """
        INSERT INTO player (team_id, first_name, last_name, birth_date, position)
        VALUES (%s, %s, %s, %s, %s)
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (p.team_id, p.first_name, p.last_name, p.birth_date, p.position))
            cnx.commit()
            return int(cur.lastrowid)

    def update(self, p: Player) -> None:
        if p.player_id is None:
            raise ValueError("player_id is required")

        sql = """
        UPDATE player
        SET team_id=%s, first_name=%s, last_name=%s, birth_date=%s, position=%s
        WHERE player_id=%s
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (p.team_id, p.first_name, p.last_name, p.birth_date, p.position, p.player_id))
            if cur.rowcount == 0:
                raise NotFoundError(f"Player {p.player_id} not found")
            cnx.commit()

    def delete(self, player_id: int) -> None:
        sql = "DELETE FROM player WHERE player_id=%s"
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (player_id,))
            if cur.rowcount == 0:
                raise NotFoundError(f"Player {player_id} not found")
            cnx.commit()
