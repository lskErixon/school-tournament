from __future__ import annotations
from dataclasses import dataclass
from contextlib import contextmanager
from typing import Optional, Any, Dict, Iterator

import mysql.connector
from mysql.connector import Error as MySqlError


@dataclass(frozen=True)
class DbConfig:
    host: str
    port: int
    user: str
    password: str
    database: str


class DbError(Exception):
    pass


class NotFoundError(DbError):
    pass


class ValidationError(DbError):
    pass


class Db:
    def __init__(self, cfg: DbConfig):
        self.cfg = cfg

    @contextmanager
    def conn(self):
        cnx = None
        try:
            cnx = mysql.connector.connect(
                host=self.cfg.host,
                port=self.cfg.port,
                user=self.cfg.user,
                password=self.cfg.password,
                database=self.cfg.database,
            )
            yield cnx
        except MySqlError as ex:
            raise DbError(f"MySQL error: {ex}") from ex
        finally:
            if cnx is not None:
                cnx.close()

    @contextmanager
    def cursor(self, cnx):
        cur = cnx.cursor(dictionary=True)
        try:
            yield cur
        finally:
            cur.close()
