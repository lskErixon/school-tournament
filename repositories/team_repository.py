from typing import List
from src.db_mysql import Db, NotFoundError
from models.team import Team


class TeamRepository:
    def __init__(self, db: Db):
        self.db = db

    def get_by_id(self, team_id: int, include_deleted: bool = False) -> Team:
        sql = """
        SELECT team_id, name, class_name, rating, is_deleted
        FROM team
        WHERE team_id=%s
        """
        if not include_deleted:
            sql += " AND is_deleted=0"

        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (team_id,))
            row = cur.fetchone()
            if not row:
                raise NotFoundError(f"Team {team_id} not found")
            return Team(**row)

    def list(self, include_deleted: bool = False) -> List[Team]:
        sql = """
        SELECT team_id, name, class_name, rating, is_deleted
        FROM team
        """
        if not include_deleted:
            sql += " WHERE is_deleted=0"
        sql += " ORDER BY class_name, name"

        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql)
            return [Team(**r) for r in cur.fetchall()]

    def insert(self, team: Team) -> int:
        sql = """
        INSERT INTO team (name, class_name, rating, is_deleted)
        VALUES (%s, %s, %s, %s)
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (team.name, team.class_name, team.rating, int(team.is_deleted)))
            cnx.commit()
            return int(cur.lastrowid)

    def update(self, team: Team) -> None:
        if team.team_id is None:
            raise ValueError("team_id is required")

        sql = """
        UPDATE team
        SET name=%s, class_name=%s, rating=%s, is_deleted=%s
        WHERE team_id=%s
        """
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (team.name, team.class_name, team.rating, int(team.is_deleted), team.team_id))
            if cur.rowcount == 0:
                raise NotFoundError(f"Team {team.team_id} not found")
            cnx.commit()

    def soft_delete(self, team_id: int) -> None:
        sql = "UPDATE team SET is_deleted=1 WHERE team_id=%s"
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (team_id,))
            if cur.rowcount == 0:
                raise NotFoundError(f"Team {team_id} not found")
            cnx.commit()

    def restore(self, team_id: int) -> None:
        sql = "UPDATE team SET is_deleted=0 WHERE team_id=%s"
        with self.db.conn() as cnx, self.db.cursor(cnx) as cur:
            cur.execute(sql, (team_id,))
            if cur.rowcount == 0:
                raise NotFoundError(f"Team {team_id} not found")
            cnx.commit()
