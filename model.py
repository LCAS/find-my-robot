import os
import sqlite3
from datetime import datetime, timezone

from flask import g

DB_PATH = os.environ.get("DB_PATH", "robots.db")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DB_PATH) as db:
        db.execute(
            """CREATE TABLE IF NOT EXISTS robots (
                name TEXT PRIMARY KEY,
                private_ip TEXT NOT NULL,
                public_ip TEXT NOT NULL,
                location TEXT,
                last_ping TEXT NOT NULL
            )"""
        )


def list_robots():
    rows = get_db().execute("SELECT * FROM robots ORDER BY name").fetchall()
    return [
        {
            "name": r["name"],
            "privateIP": r["private_ip"],
            "publicIP": r["public_ip"],
            "location": r["location"],
            "lastPing": r["last_ping"],
        }
        for r in rows
    ]


def get_robot(name):
    return get_db().execute("SELECT * FROM robots WHERE name = ?", (name,)).fetchone()


def upsert_robot(name, private_ip, public_ip, location):
    db = get_db()
    db.execute(
        """INSERT INTO robots (name, private_ip, public_ip, location, last_ping)
           VALUES (?, ?, ?, ?, ?)
           ON CONFLICT(name) DO UPDATE SET
             private_ip = excluded.private_ip,
             public_ip = excluded.public_ip,
             location = excluded.location,
             last_ping = excluded.last_ping""",
        (name, private_ip, public_ip, location, datetime.now(timezone.utc).isoformat()),
    )
    db.commit()
