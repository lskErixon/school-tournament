from typing import List
from src.db_mysql import Db
from models.match_referee import MatchReferee

class MatchRefereeRepository:
    def __init__(self, db: Db):
        self.db = db

    def list_by_match(self, match_id: int) -> List[MatchReferee]:
        sql = """
        SELECT match_id, referee_id
        FROM match_referee
        WHERE match_id=%s
        ORDER BY referee_id
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (match_id,))
            return [MatchReferee(**r) for r in cur.fetchall()]

    def add(self, link: MatchReferee) -> None:
        sql = "INSERT INTO match_referee (match_id, referee_id) VALUES (%s, %s)"
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (link.match_id, link.referee_id))
            cnx.commit()

    def remove(self, match_id: int, referee_id: int) -> None:
        sql = "DELETE FROM match_referee WHERE match_id=%s AND referee_id=%s"
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (match_id, referee_id))
            cnx.commit()

    def replace_match_referees_transaction(self, match_id: int, referee_ids: List[int]) -> None:
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            try:
                cnx.start_transaction()
                cur.execute("DELETE FROM match_referee WHERE match_id=%s", (match_id,))
                for rid in referee_ids:
                    cur.execute(
                        "INSERT INTO match_referee (match_id, referee_id) VALUES (%s, %s)",
                        (match_id, rid),
                    )
                cnx.commit()
            except Exception:
                cnx.rollback()
                raise
