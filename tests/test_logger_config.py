"""
**File:** ``test_logger_config.py``
**Region:** ``ds_common_logger_py_lib``

Description
-----------
Unit tests for the ``LoggerConfig`` class.
"""

import io
import logging
import sys
import unittest
from unittest import TestCase

from ds_common_logger_py_lib import Logger, LoggerConfig
from ds_common_logger_py_lib.formatter import ExtraFieldsFormatter


class TestLoggerConfig(TestCase):
    """Test the LoggerConfig functionality."""

    def setUp(self) -> None:
        """Set up test fixtures - reset LoggerConfig state."""
        LoggerConfig._configured = False
        LoggerConfig._prefix = ""
        LoggerConfig._format_string = None
        LoggerConfig._date_format = None
        LoggerConfig._level = logging.INFO
        LoggerConfig._handlers = []
        LoggerConfig._default_handler = None

        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(logging.NOTSET)

    def tearDown(self) -> None:
        """Clean up after tests."""
        for handler in LoggerConfig._handlers:
            if hasattr(handler, "close"):
                handler.close()
        if LoggerConfig._default_handler and hasattr(LoggerConfig._default_handler, "close"):
            LoggerConfig._default_handler.close()

    def test_configure_basic(self) -> None:
        """Test basic configuration."""
        LoggerConfig.configure(
            prefix="TestApp",
            format_string="[%(asctime)s][{prefix}][%(name)s]: %(message)s",
            level=logging.DEBUG,
        )
        self.assertTrue(LoggerConfig.is_configured())
        self.assertEqual(LoggerConfig.get_prefix(), "TestApp")

    def test_configure_with_force(self) -> None:
        """Test configuration with force=True."""
        LoggerConfig.configure(prefix="App1")
        LoggerConfig.configure(prefix="App2", force=True)
        self.assertEqual(LoggerConfig.get_prefix(), "App2")

    def test_configure_without_force_returns_early(self) -> None:
        """Test configure() returns early when already configured."""
        LoggerConfig.configure(prefix="App1")
        original_level = LoggerConfig._level
        LoggerConfig.configure(prefix="App2", force=False)
        self.assertEqual(LoggerConfig.get_prefix(), "App1")
        self.assertEqual(LoggerConfig._level, original_level)

    def test_set_prefix_without_configure(self) -> None:
        """Test set_prefix() auto-configures when not configured."""
        self.assertFalse(LoggerConfig.is_configured())
        LoggerConfig.set_prefix("MyApp")
        self.assertTrue(LoggerConfig.is_configured())
        self.assertEqual(LoggerConfig.get_prefix(), "MyApp")

    def test_set_prefix_updates_existing(self) -> None:
        """Test set_prefix() updates existing loggers."""
        LoggerConfig.configure(prefix="App1")
        logger = Logger.get_logger("test")
        LoggerConfig.set_prefix("App2")
        formatter = logger.handlers[0].formatter
        if isinstance(formatter, ExtraFieldsFormatter):
            self.assertEqual(formatter.template_vars.get("prefix"), "App2")

    def test_add_handler(self) -> None:
        """Test adding handler."""
        LoggerConfig.configure(prefix="Test")
        handler = logging.StreamHandler(io.StringIO())
        LoggerConfig.add_handler(handler)
        self.assertIn(handler, LoggerConfig._handlers)

    def test_add_handler_not_configured_raises(self) -> None:
        """Test add_handler() raises error when not configured."""
        handler = logging.StreamHandler(io.StringIO())
        with self.assertRaises(RuntimeError):
            LoggerConfig.add_handler(handler)

    def test_remove_handler(self) -> None:
        """Test removing handler."""
        LoggerConfig.configure(prefix="Test")
        handler = logging.StreamHandler(io.StringIO())
        LoggerConfig.add_handler(handler)
        LoggerConfig.remove_handler(handler)
        self.assertNotIn(handler, LoggerConfig._handlers)

    def test_set_default_handler(self) -> None:
        """Test setting default handler."""
        LoggerConfig.configure(prefix="Test")
        handler = logging.StreamHandler(sys.stderr)
        LoggerConfig.set_default_handler(handler)
        self.assertEqual(LoggerConfig._default_handler, handler)

    def test_set_default_handler_not_configured_raises(self) -> None:
        """Test set_default_handler() raises error when not configured."""
        handler = logging.StreamHandler(io.StringIO())
        with self.assertRaises(RuntimeError):
            LoggerConfig.set_default_handler(handler)

    def test_helper_methods(self) -> None:
        """Test helper methods."""
        self.assertFalse(LoggerConfig.is_configured())
        LoggerConfig.configure(prefix="Test", format_string="%(message)s", date_format="%Y-%m-%d")
        self.assertTrue(LoggerConfig.is_configured())
        self.assertEqual(LoggerConfig.get_prefix(), "Test")
        self.assertEqual(LoggerConfig.get_format_string(), "%(message)s")
        self.assertEqual(LoggerConfig.get_date_format(), "%Y-%m-%d")

    def test_create_formatter(self) -> None:
        """Test _create_formatter() creates formatter with template vars."""
        LoggerConfig.configure(prefix="TestApp", format_string="%(message)s")
        formatter = LoggerConfig._create_formatter()
        self.assertIsInstance(formatter, ExtraFieldsFormatter)
        self.assertEqual(formatter.template_vars.get("prefix"), "TestApp")

    def test_configure_with_default_handler(self) -> None:
        """Test configure() with default_handler (line 115)."""
        handler = logging.StreamHandler(io.StringIO())
        LoggerConfig.configure(prefix="Test", default_handler=handler)
        self.assertEqual(LoggerConfig._default_handler, handler)

    def test_configure_with_handlers_list(self) -> None:
        """Test configure() with handlers list (lines 117-118, 137-138)."""
        handler1 = logging.StreamHandler(io.StringIO())
        handler2 = logging.StreamHandler(io.StringIO())
        LoggerConfig.configure(prefix="Test", handlers=[handler1, handler2])
        self.assertEqual(len(LoggerConfig._handlers), 2)
        self.assertIsNone(LoggerConfig._default_handler)
        root_logger = logging.getLogger()
        self.assertIn(handler1, root_logger.handlers)
        self.assertIn(handler2, root_logger.handlers)

    def test_set_default_handler_adds_to_loggers_without_handlers(self) -> None:
        """Test set_default_handler() adds to loggers without handlers (line 262)."""
        LoggerConfig.configure(prefix="Test")
        logger = logging.getLogger("test_no_handlers")
        logger.handlers.clear()
        handler = logging.StreamHandler(io.StringIO())
        LoggerConfig.set_default_handler(handler)
        self.assertIn(handler, logger.handlers)


if __name__ == "__main__":
    unittest.main()
