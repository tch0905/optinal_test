import sqlite3

DB_NAME = "../mapping.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mappings (
            id TEXT NOT NULL,
            key TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()