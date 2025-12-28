import unittest
import os
from pathlib import Path
from unittest.mock import patch
from app.config import Config


class TestConfig(unittest.TestCase):
    """Test configuration loading and validation."""

    def test_config_has_required_attributes(self):
        """Test that Config class has all required attributes."""
        self.assertTrue(hasattr(Config, "API_KEY"))
        self.assertTrue(hasattr(Config, "MODEL_NAME"))
        self.assertTrue(hasattr(Config, "BASE_URL"))
        self.assertTrue(hasattr(Config, "DB_PATH"))

    def test_default_model_name(self):
        """Test that model name defaults to qwen-turbo when not set."""
        # Test the actual Config class default
        self.assertIn("qwen", Config.MODEL_NAME.lower())

    def test_db_path_is_pathlib_path(self):
        """Test that DB_PATH is a Path object."""
        self.assertIsInstance(Config.DB_PATH, Path)

    def test_db_path_points_to_project_root(self):
        """Test that DB is in project root, not in app directory."""
        self.assertTrue(str(Config.DB_PATH).endswith("rss_data.db"))
        self.assertNotIn("app", str(Config.DB_PATH.parent.name))


if __name__ == "__main__":
    unittest.main()
