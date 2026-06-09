import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("database.db")

def get_connection():
    """Get SQLite connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create tables if they don't exist"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS novels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            source_url TEXT UNIQUE,
            source_site TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chapters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            novel_id INTEGER NOT NULL,
            chapter_num INTEGER NOT NULL,
            title TEXT,
            content TEXT,
            crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (novel_id) REFERENCES novels(id),
            UNIQUE(novel_id, chapter_num)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            novel_id INTEGER UNIQUE NOT NULL,
            cover_url TEXT,
            description TEXT,
            status TEXT DEFAULT 'idle',
            total_chapters INTEGER DEFAULT 0,
            FOREIGN KEY (novel_id) REFERENCES novels(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS extension_registry (
            name TEXT PRIMARY KEY,
            version TEXT NOT NULL,
            enabled BOOLEAN DEFAULT 1,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()