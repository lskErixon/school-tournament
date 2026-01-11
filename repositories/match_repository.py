from __future__ import annotations
from typing import List
from src.db_mysql import Db, NotFoundError, DbError, ValidationError
from models.match import Match


class MatchRepository:
    def __init__(self, db: Db):
        self.db = db

    # -------------------------
    # Basic CRUD operations
    # -------------------------
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

            # Convert MySQL 0/1 to Python bool
            row["is_overtime"] = bool(row["is_overtime"])
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
            rows = cur.fetchall()

            for r in rows:
                r["is_overtime"] = bool(r["is_overtime"])

            return [Match(**r) for r in rows]

    def insert(self, m: Match) -> int:
        sql = """
        INSERT INTO matches (tournament_id, home_team_id, away_team_id, start_time, status, is_overtime)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(
                sql,
                (
                    m.tournament_id,
                    m.home_team_id,
                    m.away_team_id,
                    m.start_time,
                    m.status,
                    int(m.is_overtime),
                ),
            )
            cnx.commit()
            return int(cur.lastrowid)

    def update(self, m: Match) -> None:
        if m.match_id is None:
            raise ValueError("match_id is required")

        sql = """
        UPDATE matches
        SET tournament_id=%s,
            home_team_id=%s,
            away_team_id=%s,
            start_time=%s,
            status=%s,
            is_overtime=%s
        WHERE match_id=%s
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(
                sql,
                (
                    m.tournament_id,
                    m.home_team_id,
                    m.away_team_id,
                    m.start_time,
                    m.status,
                    int(m.is_overtime),
                    m.match_id,
                ),
            )
            if cur.rowcount == 0:
                raise NotFoundError(f"Match {m.match_id} not found")

            cnx.commit()

    def delete(self, match_id: int) -> None:
        """
        Deletes a match including all referee relations (match_referee).
        This prevents foreign key constraint errors.
        """
        with self.db.conn() as cnx:
            try:
                cnx.start_transaction()

                with self.db.cursor(cnx) as cur:
                    # Delete M:N relations first
                    cur.execute("DELETE FROM match_referee WHERE match_id=%s", (match_id,))

                    # Delete the match itself
                    cur.execute("DELETE FROM matches WHERE match_id=%s", (match_id,))
                    if cur.rowcount == 0:
                        raise NotFoundError(f"Match {match_id} not found")

                cnx.commit()

            except Exception as e:
                cnx.rollback()
                if isinstance(e, (NotFoundError, ValidationError, DbError)):
                    raise
                raise DbError(f"Failed to delete match {match_id}: {e}") from e

    # -------------------------
    # D1 requirement:
    # One UI action -> multiple tables
    # Transaction over matches + match_referee
    # -------------------------
    def create_match_with_referees(self, m: Match, referee_ids: List[int]) -> int:
        """
        Transaction:
          1) Insert into matches
          2) Insert into match_referee (M:N relation)
        """
        if not referee_ids:
            raise ValidationError("At least one referee must be selected.")
        if m.home_team_id == m.away_team_id:
            raise ValidationError("Home and Away teams must be different.")

        with self.db.conn() as cnx:
            try:
                cnx.start_transaction()

                with self.db.cursor(cnx) as cur:
                    cur.execute(
                        """
                        INSERT INTO matches
                        (tournament_id, home_team_id, away_team_id, start_time, status, is_overtime)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (
                            m.tournament_id,
                            m.home_team_id,
                            m.away_team_id,
                            m.start_time,
                            m.status,
                            int(m.is_overtime),
                        ),
                    )
                    match_id = int(cur.lastrowid)

                    cur.executemany(
                        """
                        INSERT INTO match_referee (match_id, referee_id)
                        VALUES (%s, %s)
                        """,
                        [(match_id, rid) for rid in referee_ids],
                    )

                cnx.commit()
                return match_id

            except Exception as e:
                cnx.rollback()
                if isinstance(e, (NotFoundError, ValidationError, DbError)):
                    raise
                raise DbError(f"Failed to create match with referees: {e}") from e

    def set_referees(self, match_id: int, referee_ids: List[int]) -> None:
        """
        Replaces all referees for a match using a transaction.
        """
        if not referee_ids:
            raise ValidationError("At least one referee must be selected.")

        with self.db.conn() as cnx:
            try:
                cnx.start_transaction()

                with self.db.cursor(cnx) as cur:
                    # Ensure match exists
                    cur.execute("SELECT match_id FROM matches WHERE match_id=%s", (match_id,))
                    if not cur.fetchone():
                        raise NotFoundError(f"Match {match_id} not found")

                    # Replace relations
                    cur.execute("DELETE FROM match_referee WHERE match_id=%s", (match_id,))
                    cur.executemany(
                        "INSERT INTO match_referee (match_id, referee_id) VALUES (%s, %s)",
                        [(match_id, rid) for rid in referee_ids],
                    )

                cnx.commit()

            except Exception as e:
                cnx.rollback()
                if isinstance(e, (NotFoundError, ValidationError, DbError)):
                    raise
                raise DbError(f"Failed to set referees for match {match_id}: {e}") from e

    # -------------------------
    # Listing for GUI (with joined names)
    # -------------------------
    def list_with_names(self) -> list[dict]:
        """
        Returns matches with tournament and team names for GUI tables.
        LEFT JOIN is used to avoid crashes during test deletions.
        """
        sql = """
        SELECT
            m.match_id,
            t.name AS tournament_name,
            ht.name AS home_team_name,
            at.name AS away_team_name,
            DATE_FORMAT(m.start_time, '%%Y-%%m-%%d %%H:%%i') AS start_time,
            m.status,
            m.is_overtime
        FROM matches m
        LEFT JOIN tournament t ON t.tournament_id = m.tournament_id
        LEFT JOIN team ht ON ht.team_id = m.home_team_id
        LEFT JOIN team at ON at.team_id = m.away_team_id
        ORDER BY m.start_time DESC, m.match_id DESC
        LIMIT 200
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql)
            rows = list(cur.fetchall())
            for r in rows:
                r["is_overtime"] = bool(r["is_overtime"])
            return rows

    def get_referee_ids(self, match_id: int) -> List[int]:
        """
        Returns referee IDs assigned to a match.
        """
        sql = """
        SELECT referee_id
        FROM match_referee
        WHERE match_id=%s
        ORDER BY referee_id
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (match_id,))
            return [int(r["referee_id"]) for r in cur.fetchall()]
