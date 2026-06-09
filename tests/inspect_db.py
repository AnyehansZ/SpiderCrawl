import sqlite3
from pathlib import Path
import json

DB_PATH = Path("database.db")

def inspect_db():
    """Display all database contents"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("\n=== NOVELS ===")
    cursor.execute("SELECT * FROM novels")
    for row in cursor.fetchall():
        print(dict(row))
    
    print("\n=== CHAPTERS ===")
    cursor.execute("SELECT id, novel_id, chapter_num, title FROM chapters")
    for row in cursor.fetchall():
        print(dict(row))
    
    print("\n=== METADATA ===")
    cursor.execute("SELECT * FROM metadata")
    for row in cursor.fetchall():
        print(dict(row))
    
    conn.close()

if __name__ == "__main__":
    inspect_db()