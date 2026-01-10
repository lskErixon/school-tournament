from typing import List
from src.db_mysql import Db, NotFoundError
from models.match import Match


class MatchRepository:
    def __init__(self, db: Db):
        self.db = db

    def get_by_id(self, match_id: int) -> Match:
        sql = """
        SELECT match_id, tournament_id, home_team_id, away_team_id, start_time, status, is_overtime
        FROM matches
        WHERE match_id=%s
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (match_id,))
            row = cur.fetchone()
            if not row:
                raise NotFoundError(f"Match {match_id} not found")
            return Match(**row)

    def list_by_tournament(self, tournament_id: int) -> List[Match]:
        sql = """
        SELECT match_id, tournament_id, home_team_id, away_team_id, start_time, status, is_overtime
        FROM matches
        WHERE tournament_id=%s
        ORDER BY start_time DESC
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (tournament_id,))
            return [Match(**r) for r in cur.fetchall()]

    def insert(self, m: Match) -> int:
        sql = """
        INSERT INTO matches (tournament_id, home_team_id, away_team_id, start_time, status, is_overtime)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (m.tournament_id, m.home_team_id, m.away_team_id, m.start_time, m.status, int(m.is_overtime)))
            cnx.commit()
            return int(cur.lastrowid)

    def update(self, m: Match) -> None:
        if m.match_id is None:
            raise ValueError("match_id is required")

        sql = """
        UPDATE matches
        SET tournament_id=%s, home_team_id=%s, away_team_id=%s, start_time=%s, status=%s, is_overtime=%s
        WHERE match_id=%s
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (m.tournament_id, m.home_team_id, m.away_team_id, m.start_time, m.status, int(m.is_overtime), m.match_id))
            if cur.rowcount == 0:
                raise NotFoundError(f"Match {m.match_id} not found")
            cnx.commit()

    def delete(self, match_id: int) -> None:
        sql = "DELETE FROM matches WHERE match_id=%s"
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (match_id,))
            if cur.rowcount == 0:
                raise NotFoundError(f"Match {match_id} not found")
            cnx.commit()
