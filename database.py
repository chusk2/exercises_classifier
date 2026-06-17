import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "classifications.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ejercicios (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                asignatura   TEXT    NOT NULL,
                tema         TEXT    NOT NULL,
                año          INTEGER NOT NULL,
                convocatoria TEXT    NOT NULL,
                ejercicio    TEXT    NOT NULL,
                tipo_ejercicio TEXT  NOT NULL
            )
        """)
        conn.commit()


def insert_ejercicio(asignatura, tema, año, convocatoria, ejercicio, tipo_ejercicio):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO ejercicios (asignatura, tema, año, convocatoria, ejercicio, tipo_ejercicio)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (asignatura, tema, año, convocatoria, ejercicio, tipo_ejercicio),
        )
        conn.commit()


def get_all_ejercicios():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM ejercicios").fetchall()
    return [dict(row) for row in rows]

