"""
**File:** ``test_logger_config.py``
**Region:** ``ds_common_logger_py_lib``

Description
-----------
Unit tests for the ``Logger`` configuration functionality.
"""

import io
import logging
import sys
import unittest
from unittest import TestCase

from ds_common_logger_py_lib import Logger
from ds_common_logger_py_lib.formatter import ExtraFieldsFormatter, LoggerFilter


class TestLoggerConfig(TestCase):
    """Test the Logger configuration functionality."""

    def setUp(self) -> None:
        """Set up test fixtures - reset Logger state."""
        Logger._configured = False
        Logger._prefix = ""
        Logger._format_string = None
        Logger._date_format = None
        Logger._level = logging.INFO
        Logger._handlers = []
        Logger._default_handler = None
        Logger._managed_loggers.clear()
        Logger._logger_levels = {}

        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(logging.NOTSET)

    def tearDown(self) -> None:
        """Clean up after tests."""
        for handler in Logger._handlers:
            if hasattr(handler, "close"):
                handler.close()
        if Logger._default_handler and hasattr(Logger._default_handler, "close"):
            Logger._default_handler.close()

    def test_configure_basic(self) -> None:
        """Test basic configuration."""
        Logger.configure(
            prefix="TestApp",
            format_string="[%(asctime)s][{prefix}][%(name)s]: %(message)s",
            level=logging.DEBUG,
        )
        self.assertTrue(Logger.is_configured())
        self.assertEqual(Logger.get_prefix(), "TestApp")

    def test_configure_with_force(self) -> None:
        """Test configuration with force=True."""
        Logger.configure(prefix="App1")
        Logger.configure(prefix="App2", force=True)
        self.assertEqual(Logger.get_prefix(), "App2")

    def test_configure_without_force_returns_early(self) -> None:
        """Test configure() returns early when already configured."""
        Logger.configure(prefix="App1")
        original_level = Logger._level
        Logger.configure(prefix="App2", force=False)
        self.assertEqual(Logger.get_prefix(), "App1")
        self.assertEqual(Logger._level, original_level)

    def test_set_prefix_without_configure(self) -> None:
        """Test set_prefix() auto-configures when not configured."""
        self.assertFalse(Logger.is_configured())
        Logger.set_prefix("MyApp")
        self.assertTrue(Logger.is_configured())
        self.assertEqual(Logger.get_prefix(), "MyApp")

    def test_set_prefix_updates_existing(self) -> None:
        """Test set_prefix() updates existing loggers."""
        Logger.configure(prefix="App1")
        Logger.get_logger("test")
        Logger.set_prefix("App2")
        root_logger = logging.getLogger()
        self.assertGreater(len(root_logger.handlers), 0)
        formatter = root_logger.handlers[0].formatter
        if isinstance(formatter, ExtraFieldsFormatter):
            self.assertEqual(formatter.template_vars.get("prefix"), "App2")

    def test_add_handler(self) -> None:
        """Test adding handler."""
        Logger.configure(prefix="Test")
        handler = logging.StreamHandler(io.StringIO())
        Logger.add_handler(handler)
        self.assertIn(handler, Logger._handlers)

        self.assertIsInstance(handler.formatter, ExtraFieldsFormatter)
        self.assertTrue(any(isinstance(f, LoggerFilter) for f in handler.filters))

    def test_add_handler_not_configured_raises(self) -> None:
        """Test add_handler() raises error when not configured."""
        handler = logging.StreamHandler(io.StringIO())
        with self.assertRaises(RuntimeError):
            Logger.add_handler(handler)

    def test_external_handler_level_preserved(self) -> None:
        """Test Logger does not override external handler level."""
        external_stream = io.StringIO()
        external_handler = logging.StreamHandler(external_stream)
        external_handler.setLevel(logging.ERROR)
        external_formatter = logging.Formatter("%(message)s")
        external_handler.setFormatter(external_formatter)

        root_logger = logging.getLogger()
        root_logger.addHandler(external_handler)

        Logger.configure(prefix="Test")

        self.assertEqual(external_handler.level, logging.ERROR)
        self.assertIs(external_handler.formatter, external_formatter)

    def test_remove_handler(self) -> None:
        """Test removing handler."""
        Logger.configure(prefix="Test")
        handler = logging.StreamHandler(io.StringIO())
        Logger.add_handler(handler)
        Logger.remove_handler(handler)
        self.assertNotIn(handler, Logger._handlers)

    def test_set_default_handler(self) -> None:
        """Test setting default handler."""
        Logger.configure(prefix="Test")
        handler = logging.StreamHandler(sys.stderr)
        Logger.set_default_handler(handler)
        self.assertEqual(Logger._default_handler, handler)

    def test_set_default_handler_not_configured_raises(self) -> None:
        """Test set_default_handler() raises error when not configured."""
        handler = logging.StreamHandler(io.StringIO())
        with self.assertRaises(RuntimeError):
            Logger.set_default_handler(handler)

    def test_helper_methods(self) -> None:
        """Test helper methods."""
        self.assertFalse(Logger.is_configured())
        Logger.configure(prefix="Test", format_string="%(message)s", date_format="%Y-%m-%d")
        self.assertTrue(Logger.is_configured())
        self.assertEqual(Logger.get_prefix(), "Test")
        self.assertEqual(Logger.get_format_string(), "%(message)s")
        self.assertEqual(Logger.get_date_format(), "%Y-%m-%d")

    def test_create_formatter(self) -> None:
        """Test _create_formatter() creates formatter with template vars."""
        Logger.configure(prefix="TestApp", format_string="%(message)s")
        formatter = Logger._create_formatter()
        self.assertIsInstance(formatter, ExtraFieldsFormatter)
        self.assertEqual(formatter.template_vars.get("prefix"), "TestApp")

    def test_configure_with_default_handler(self) -> None:
        """Test configure() with default_handler."""
        handler = logging.StreamHandler(io.StringIO())
        Logger.configure(prefix="Test", default_handler=handler)
        self.assertEqual(Logger._default_handler, handler)

    def test_configure_with_handlers_list(self) -> None:
        """Test configure() with handlers list."""
        handler1 = logging.StreamHandler(io.StringIO())
        handler2 = logging.StreamHandler(io.StringIO())
        Logger.configure(prefix="Test", handlers=[handler1, handler2])
        self.assertEqual(len(Logger._handlers), 2)
        self.assertIsNone(Logger._default_handler)
        root_logger = logging.getLogger()
        self.assertIn(handler1, root_logger.handlers)
        self.assertIn(handler2, root_logger.handlers)


if __name__ == "__main__":
    unittest.main()
