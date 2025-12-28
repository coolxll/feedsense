import sqlite3
from pathlib import Path
from contextlib import contextmanager
from .config import config


def init_db():
    """Initialize the database tables."""
    conn = sqlite3.connect(config.DB_PATH)
    c = conn.cursor()

    # Check if tables exist, if not create them

    # Table: Feeds
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS feeds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        url TEXT UNIQUE NOT NULL,
        last_fetched TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    )
    """
    )

    # Table: Articles
    # score: 0-10 integer score from LLM
    # analysis: Text reasoning from LLM
    # status: 'new', 'analyzed', 'read', 'skipped'
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        feed_id INTEGER,
        title TEXT,
        link TEXT UNIQUE NOT NULL,
        published TIMESTAMP,
        summary TEXT,
        content TEXT,
        
        status TEXT DEFAULT 'new',
        score INTEGER DEFAULT 0,
        analysis TEXT,
        category TEXT,
        
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(feed_id) REFERENCES feeds(id)
    )
    """
    )

    conn.commit()
    conn.close()


@contextmanager
def get_db():
    """Context manager for database connection."""
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    try:
        yield conn
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {config.DB_PATH}")
