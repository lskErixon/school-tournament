from __future__ import annotations

from typing import List

from src.db_mysql import Db, NotFoundError
from models.referee import Referee


class RefereeRepository:
    def __init__(self, db: Db):
        self.db = db

    def get_by_id(self, referee_id: int) -> Referee:
        sql = """
        SELECT referee_id, full_name, email, level, active
        FROM referee
        WHERE referee_id=%s
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (referee_id,))
            row = cur.fetchone()
            if not row:
                raise NotFoundError(f"Referee {referee_id} not found")

            row["active"] = bool(row["active"])
            return Referee(**row)

    def list(self, active_only: bool = False) -> List[Referee]:
        """
        Returns list of referees.
        If active_only=True, only active referees are returned.
        """
        if active_only:
            sql = """
            SELECT referee_id, full_name, email, level, active
            FROM referee
            WHERE active=1
            ORDER BY full_name
            """
            params = ()
        else:
            sql = """
            SELECT referee_id, full_name, email, level, active
            FROM referee
            ORDER BY full_name
            """
            params = ()

        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()

            for r in rows:
                r["active"] = bool(r["active"])

            return [Referee(**r) for r in rows]

    def insert(self, r: Referee) -> int:
        sql = """
        INSERT INTO referee (full_name, email, level, active)
        VALUES (%s, %s, %s, %s)
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(
                sql,
                (r.full_name, r.email, r.level, int(r.active)),
            )
            cnx.commit()
            return int(cur.lastrowid)

    def update(self, r: Referee) -> None:
        if r.referee_id is None:
            raise ValueError("referee_id is required")

        sql = """
        UPDATE referee
        SET full_name=%s,
            email=%s,
            level=%s,
            active=%s
        WHERE referee_id=%s
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(
                sql,
                (r.full_name, r.email, r.level, int(r.active), r.referee_id),
            )
            if cur.rowcount == 0:
                raise NotFoundError(f"Referee {r.referee_id} not found")
            cnx.commit()

    def delete(self, referee_id: int) -> None:
        sql = "DELETE FROM referee WHERE referee_id=%s"
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (referee_id,))
            if cur.rowcount == 0:
                raise NotFoundError(f"Referee {referee_id} not found")
            cnx.commit()
