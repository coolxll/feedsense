import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from app.services.rss import RSSService
from app.db import init_db
from app.config import Config


class TestRSSService(unittest.TestCase):
    """Test RSS service functionality."""

    def setUp(self):
        """Set up test database and RSS service."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db_path = Path(self.temp_db.name)
        self.temp_db.close()

        self.patcher = patch.object(Config, "DB_PATH", self.temp_db_path)
        self.patcher.start()

        init_db()
        self.service = RSSService()

    def tearDown(self):
        """Clean up."""
        self.patcher.stop()
        if self.temp_db_path.exists():
            self.temp_db_path.unlink()

    @patch("app.services.rss.feedparser.parse")
    def test_add_feed_success(self, mock_parse):
        """Test successfully adding a feed."""
        # Mock feedparser response
        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_feed.feed.get.return_value = "Test Feed"
        mock_parse.return_value = mock_feed

        result = self.service.add_feed("http://example.com/feed")
        self.assertTrue(result)

    @patch("app.services.rss.feedparser.parse")
    def test_add_duplicate_feed(self, mock_parse):
        """Test adding duplicate feed fails gracefully."""
        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_feed.feed.get.return_value = "Test Feed"
        mock_parse.return_value = mock_feed

        # Add first time
        self.service.add_feed("http://example.com/feed")

        # Try to add again
        result = self.service.add_feed("http://example.com/feed")
        self.assertFalse(result)

    def test_list_feeds_empty(self):
        """Test listing feeds when none exist."""
        feeds = self.service.list_feeds()
        self.assertEqual(len(feeds), 0)

    @patch("app.services.rss.feedparser.parse")
    def test_list_feeds_with_data(self, mock_parse):
        """Test listing feeds after adding some."""
        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_feed.feed.get.return_value = "Test Feed"
        mock_parse.return_value = mock_feed

        self.service.add_feed("http://example.com/feed")
        feeds = self.service.list_feeds()

        self.assertEqual(len(feeds), 1)
        self.assertEqual(feeds[0]["url"], "http://example.com/feed")

    @patch("app.services.rss.feedparser.parse")
    def test_fetch_all_with_new_entries(self, mock_parse):
        """Test fetching articles from feeds."""
        # Setup: Add a feed first
        mock_feed_add = MagicMock()
        mock_feed_add.bozo = False
        mock_feed_add.feed.get.return_value = "Test Feed"
        mock_parse.return_value = mock_feed_add
        self.service.add_feed("http://example.com/feed")

        # Mock fetch response with entries
        mock_feed_fetch = MagicMock()
        mock_feed_fetch.entries = [
            {
                "title": "Test Article",
                "link": "http://example.com/article1",
                "summary": "Test summary",
                "published_parsed": None,
            }
        ]
        mock_parse.return_value = mock_feed_fetch

        count = self.service.fetch_all()
        self.assertEqual(count, 1)

    @patch("app.services.rss.feedparser.parse")
    def test_fetch_all_skips_duplicates(self, mock_parse):
        """Test that duplicate articles are not added."""
        # Add feed
        mock_feed_add = MagicMock()
        mock_feed_add.bozo = False
        mock_feed_add.feed.get.return_value = "Test Feed"
        mock_parse.return_value = mock_feed_add
        self.service.add_feed("http://example.com/feed")

        # Mock same article twice
        mock_feed_fetch = MagicMock()
        mock_feed_fetch.entries = [
            {
                "title": "Test Article",
                "link": "http://example.com/article1",
                "summary": "Test summary",
                "published_parsed": None,
            }
        ]
        mock_parse.return_value = mock_feed_fetch

        # First fetch
        count1 = self.service.fetch_all()
        self.assertEqual(count1, 1)

        # Second fetch (same article)
        count2 = self.service.fetch_all()
        self.assertEqual(count2, 0)  # Should skip duplicate


if __name__ == "__main__":
    unittest.main()
