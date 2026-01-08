import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data.db"


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS forms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                city TEXT NOT NULL,
                goal TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.commit()


def save_form(user_id: int, username: str | None, name: str, age: int, city: str, goal: str) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO forms (user_id, username, name, age, city, goal)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, username, name, age, city, goal),
        )
        conn.commit()
def get_last_forms(limit: int = 5):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, user_id, username, name, age, city, goal, created_at
            FROM forms
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return rows
import csv

def export_forms_to_csv(filepath: str) -> int:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, user_id, username, name, age, city, goal, created_at
            FROM forms
            ORDER BY id DESC
            """
        ).fetchall()

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "user_id", "username", "name", "age", "city", "goal", "created_at"])
        for r in rows:
            writer.writerow([r["id"], r["user_id"], r["username"], r["name"], r["age"], r["city"], r["goal"], r["created_at"]])

    return len(rows)
