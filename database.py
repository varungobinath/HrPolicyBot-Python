import sqlite3

from config import SQLITE_PATH


def get_connection():
    return sqlite3.connect(SQLITE_PATH)


def init_db():
    conn = get_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            answer TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()


def save_history(question, answer):
    conn = get_connection()

    conn.execute(
        "INSERT INTO history (question, answer) VALUES (?, ?)",
        (question, answer),
    )

    conn.commit()
    conn.close()


def get_all_history():
    conn = get_connection()

    cursor = conn.execute(
        "SELECT id, question, answer, created_at FROM history ORDER BY id DESC"
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_history_item(entry_id):
    conn = get_connection()

    cursor = conn.execute(
        "SELECT id, question, answer, created_at FROM history WHERE id = ?",
        (entry_id,),
    )

    row = cursor.fetchone()

    conn.close()

    return row


def delete_history(entry_id):
    conn = get_connection()

    conn.execute(
        "DELETE FROM history WHERE id = ?",
        (entry_id,),
    )

    conn.commit()
    conn.close()