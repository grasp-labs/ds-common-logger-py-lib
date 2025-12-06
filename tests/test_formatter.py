"""
File: test_formatter.py
Description: Test the ExtraFieldsFormatter functionality for the DS shared logger package.
Region: packages/logging/python/tests

# Example:

from ds_common_logger_py_lib.formatter import ExtraFieldsFormatter
import logging

formatter = ExtraFieldsFormatter()
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger("test")
logger.addHandler(handler)
logger.info("Test message", extra={"user_id": 123})
"""

import io
import logging
import unittest
from unittest import TestCase
from unittest.mock import patch

from ds_common_logger_py_lib.formatter import ExtraFieldsFormatter


class TestFormatter(TestCase):
    """Test the ExtraFieldsFormatter functionality."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.formatter = ExtraFieldsFormatter()
        self.stream = io.StringIO()
        self.handler = logging.StreamHandler(self.stream)
        self.handler.setFormatter(self.formatter)
        self.logger = logging.getLogger("test_formatter")
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.INFO)

    def test_formatter_with_extra_fields(self) -> None:
        """Test formatter includes extra fields in output."""
        self.logger.info("Test message", extra={"user_id": 123, "action": "login"})
        output = self.stream.getvalue()
        self.assertIn("Test message", output)
        self.assertIn("extra:", output)
        self.assertIn("user_id", output)

    def test_formatter_without_extra_fields(self) -> None:
        """Test formatter works without extra fields."""
        self.logger.info("Simple message")
        output = self.stream.getvalue()
        self.assertIn("Simple message", output)
        self.assertNotIn("extra:", output)

    def test_formatter_with_json_serializable_extra(self) -> None:
        """Test formatter serializes extra fields as JSON."""
        self.logger.info("Test", extra={"key": "value", "number": 42})
        output = self.stream.getvalue()
        # Should contain JSON-like structure
        self.assertIn("key", output)
        self.assertIn("value", output)

    def test_formatter_handles_serialization_error(self) -> None:
        """Test formatter handles non-serializable objects gracefully."""

        def unserializable_func() -> None:
            pass

        # Mock json.dumps to raise an error to test error handling path
        with patch("ds_common_logger_py_lib.formatter.json.dumps", side_effect=TypeError("Cannot serialize")):
            self.logger.info("Test", extra={"obj": unserializable_func})
            output = self.stream.getvalue()

            self.assertIn("Test", output)
            self.assertIn("extra:", output)
            self.assertIn("obj", output)


if __name__ == "__main__":
    unittest.main()
