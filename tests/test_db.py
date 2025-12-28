import unittest
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch
from app.db import init_db, get_db
from app.config import Config


class TestDatabase(unittest.TestCase):
    """Test database initialization and operations."""

    def setUp(self):
        """Create a temporary database for testing."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db_path = Path(self.temp_db.name)
        self.temp_db.close()

        # Patch the config to use temp database
        self.patcher = patch.object(Config, "DB_PATH", self.temp_db_path)
        self.patcher.start()

    def tearDown(self):
        """Clean up temporary database."""
        self.patcher.stop()
        if self.temp_db_path.exists():
            self.temp_db_path.unlink()

    def test_init_db_creates_tables(self):
        """Test that init_db creates required tables."""
        init_db()

        conn = sqlite3.connect(self.temp_db_path)
        cursor = conn.cursor()

        # Check feeds table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='feeds'"
        )
        self.assertIsNotNone(cursor.fetchone())

        # Check articles table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='articles'"
        )
        self.assertIsNotNone(cursor.fetchone())

        conn.close()

    def test_feeds_table_schema(self):
        """Test that feeds table has correct columns."""
        init_db()

        conn = sqlite3.connect(self.temp_db_path)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(feeds)")
        columns = {row[1] for row in cursor.fetchall()}

        expected_columns = {"id", "name", "url", "last_fetched", "is_active"}
        self.assertTrue(expected_columns.issubset(columns))

        conn.close()

    def test_articles_table_schema(self):
        """Test that articles table has correct columns."""
        init_db()

        conn = sqlite3.connect(self.temp_db_path)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(articles)")
        columns = {row[1] for row in cursor.fetchall()}

        expected_columns = {
            "id",
            "feed_id",
            "title",
            "link",
            "status",
            "score",
            "analysis",
            "category",
        }
        self.assertTrue(expected_columns.issubset(columns))

        conn.close()

    def test_get_db_context_manager(self):
        """Test that get_db works as context manager."""
        init_db()

        with get_db() as conn:
            self.assertIsInstance(conn, sqlite3.Connection)
            # Test that we can execute queries
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            self.assertGreater(len(tables), 0)


if __name__ == "__main__":
    unittest.main()
