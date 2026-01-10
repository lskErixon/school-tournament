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
            return Referee(**row)

    def list(self, only_active: bool = False) -> List[Referee]:
        sql = """
        SELECT referee_id, full_name, email, level, active
        FROM referee
        """
        if only_active:
            sql += " WHERE active=1"
        sql += " ORDER BY full_name"

        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql)
            return [Referee(**r) for r in cur.fetchall()]

    def insert(self, r: Referee) -> int:
        sql = """
        INSERT INTO referee (full_name, email, level, active)
        VALUES (%s, %s, %s, %s)
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (r.full_name, r.email, r.level, int(r.active)))
            cnx.commit()
            return int(cur.lastrowid)

    def update(self, r: Referee) -> None:
        if r.referee_id is None:
            raise ValueError("referee_id is required")

        sql = """
        UPDATE referee
        SET full_name=%s, email=%s, level=%s, active=%s
        WHERE referee_id=%s
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (r.full_name, r.email, r.level, int(r.active), r.referee_id))
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
