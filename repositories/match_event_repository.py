from typing import List, Optional
from datetime import datetime
from src.db_mysql import Db, NotFoundError, ValidationError
from models.match_event import MatchEvent


class MatchEventRepository:
    def __init__(self, db: Db):
        self.db = db

    def get_by_id(self, event_id: int) -> MatchEvent:
        sql = """
        SELECT event_id, match_id, player_id, team_id, minute, event_type, xg, created_at
        FROM match_event
        WHERE event_id=%s
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (event_id,))
            row = cur.fetchone()
            if not row:
                raise NotFoundError(f"MatchEvent {event_id} not found")
            return MatchEvent(**row)

    def list_by_match(self, match_id: int) -> List[MatchEvent]:
        sql = """
        SELECT event_id, match_id, player_id, team_id, minute, event_type, xg, created_at
        FROM match_event
        WHERE match_id=%s
        ORDER BY minute, created_at
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (match_id,))
            return [MatchEvent(**r) for r in cur.fetchall()]

    def insert(self, e: MatchEvent) -> int:
        sql = """
        INSERT INTO match_event (match_id, player_id, team_id, minute, event_type, xg, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (e.match_id, e.player_id, e.team_id, e.minute, e.event_type, e.xg, e.created_at))
            cnx.commit()
            return int(cur.lastrowid)

    def update(self, e: MatchEvent) -> None:
        if e.event_id is None:
            raise ValueError("event_id is required")

        sql = """
        UPDATE match_event
        SET match_id=%s, player_id=%s, team_id=%s, minute=%s, event_type=%s, xg=%s, created_at=%s
        WHERE event_id=%s
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (e.match_id, e.player_id, e.team_id, e.minute, e.event_type, e.xg, e.created_at, e.event_id))
            if cur.rowcount == 0:
                raise NotFoundError(f"MatchEvent {e.event_id} not found")
            cnx.commit()

    def delete(self, event_id: int) -> None:
        sql = "DELETE FROM match_event WHERE event_id=%s"
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (event_id,))
            if cur.rowcount == 0:
                raise NotFoundError(f"MatchEvent {event_id} not found")
            cnx.commit()

    # ✅ Transakce: vlož "goal" + když zápas scheduled -> nastav live
    def add_goal_transaction(
        self,
        match_id: int,
        team_id: int,
        player_id: Optional[int],
        minute: int,
        xg: Optional[float] = None
    ) -> int:
        if minute < 0 or minute > 200:
            raise ValidationError("minute out of range (0..200)")

        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            try:
                cnx.start_transaction()

                cur.execute("SELECT status FROM matches WHERE match_id=%s FOR UPDATE", (match_id,))
                row = cur.fetchone()
                if not row:
                    raise NotFoundError(f"Match {match_id} not found")

                if row["status"] in ("finished", "cancelled"):
                    raise ValidationError("cannot add event to finished/cancelled match")

                now = datetime.utcnow()
                cur.execute(
                    """
                    INSERT INTO match_event (match_id, player_id, team_id, minute, event_type, xg, created_at)
                    VALUES (%s, %s, %s, %s, 'goal', %s, %s)
                    """,
                    (match_id, player_id, team_id, minute, xg, now),
                )
                event_id = int(cur.lastrowid)

                if row["status"] == "scheduled":
                    cur.execute("UPDATE matches SET status='live' WHERE match_id=%s", (match_id,))

                cnx.commit()
                return event_id

            except Exception:
                cnx.rollback()
                raise
