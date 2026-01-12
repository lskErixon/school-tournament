import json
import sys

from db_mysql import Db, DbConfig, DbError
from ui.app import App

def load_config(path: str) -> DbConfig:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        db = data["database"]

        return DbConfig(
            host=db["host"],
            port=int(db["port"]),
            user=db["user"],
            password=db["password"],
            database=db["name"],
        )

    except FileNotFoundError:
        print("❌ Config file not found")
        sys.exit(1)

    except KeyError as e:
        print(f"❌ Missing config key: {e}")
        sys.exit(1)

    except json.JSONDecodeError:
        print("❌ Invalid JSON format in config")
        sys.exit(1)


def test_connection(db: Db) -> None:
    with db.conn() as cnx, db.cursor(cnx) as cur:
        cur.execute("SELECT 1 AS ok")
        result = cur.fetchone()
        print("Database connected:", result["ok"])


def main():
    print("Connecting to database...")

    cfg = load_config("config.json")
    db = Db(cfg)

    try:
        test_connection(db)
        print("Connection successful")
    except DbError as e:
        print("Database error:", e)
        print("Application will still start (DB test available in GUI)")

    app = App(db)
    app.mainloop()


if __name__ == "__main__":
    main()
