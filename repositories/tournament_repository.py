from typing import List
from src.db_mysql import Db, NotFoundError
from models.tournament import Tournament


class TournamentRepository:
    def __init__(self, db: Db):
        self.db = db

    def get_by_id(self, tournament_id: int) -> Tournament:
        sql = """
        SELECT tournament_id, name, start_date, end_date, is_active
        FROM tournament
        WHERE tournament_id=%s
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (tournament_id,))
            row = cur.fetchone()
            if not row:
                raise NotFoundError(f"Tournament {tournament_id} not found")
            return Tournament(**row)

    def list(self) -> List[Tournament]:
        sql = """
        SELECT tournament_id, name, start_date, end_date, is_active
        FROM tournament
        ORDER BY start_date DESC
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql)
            return [Tournament(**r) for r in cur.fetchall()]

    def insert(self, t: Tournament) -> int:
        sql = """
        INSERT INTO tournament (name, start_date, end_date, is_active)
        VALUES (%s, %s, %s, %s)
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (t.name, t.start_date, t.end_date, int(t.is_active)))
            cnx.commit()
            return int(cur.lastrowid)

    def update(self, t: Tournament) -> None:
        if t.tournament_id is None:
            raise ValueError("tournament_id is required")

        sql = """
        UPDATE tournament
        SET name=%s, start_date=%s, end_date=%s, is_active=%s
        WHERE tournament_id=%s
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (t.name, t.start_date, t.end_date, int(t.is_active), t.tournament_id))
            if cur.rowcount == 0:
                raise NotFoundError(f"Tournament {t.tournament_id} not found")
            cnx.commit()

    def delete(self, tournament_id: int) -> None:
        sql = "DELETE FROM tournament WHERE tournament_id=%s"
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (tournament_id,))
            if cur.rowcount == 0:
                raise NotFoundError(f"Tournament {tournament_id} not found")
            cnx.commit()
