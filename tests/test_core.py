"""
**File:** ``test_core.py``
**Region:** ``ds_common_logger_py_lib``

Description
-----------
Unit tests for the core ``Logger`` helper, covering configuration, logger
creation, handler behavior, format updates, and extra fields support.
"""

import io
import logging
import unittest
from unittest import TestCase

from ds_common_logger_py_lib import Logger, LoggerConfig
from ds_common_logger_py_lib.formatter import ExtraFieldsFormatter


class TestLogging(TestCase):
    """
    Test the logging functionality.

    Example:
        >>> test = TestLogging()
        >>> test.test_logging_with_extra()
    """

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Reset LoggerConfig
        LoggerConfig._configured = False
        LoggerConfig._prefix = ""
        LoggerConfig._format_string = None
        LoggerConfig._date_format = None
        LoggerConfig._level = logging.INFO
        LoggerConfig._handlers = []
        LoggerConfig._default_handler = None

        # Reset root logger to clean state
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(logging.NOTSET)

    def test_logging_with_extra(self) -> None:
        """
        Test that logging with extra fields works correctly.

        Example:
            >>> logger = Logger.get_logger(__name__)
            >>> logger.info("Test", extra={"key": "value"})
        """
        Logger()
        logger = Logger.get_logger(__name__)

        logger.info("Test info message", extra={"test": "info", "number": 42, "boolean": True})
        logger.warning("Test warning message", extra={"test": "warning", "error_code": 404})
        logger.error("Test error message", extra={"test": "error", "exception": "TestException"})

        complex_data = {
            "user": {"id": 123, "name": "Test User", "active": True},
            "metadata": {"timestamp": "2025-06-29T15:50:00", "version": "1.0.0"},
        }

        logger.info("Test with complex data", extra={"data": complex_data})

    def test_logger_initialization(self) -> None:
        """
        Test logger initialization with different parameters.

        Example:
            >>> Logger(level=logging.DEBUG)
            <ds_common_logger_py_lib.core.Logger object at ...>
        """
        logger_config = Logger()
        self.assertEqual(logger_config.level, logging.INFO)

        logger_config_debug = Logger(level=logging.DEBUG)
        self.assertEqual(logger_config_debug.level, logging.DEBUG)

        custom_format = "%(name)s - %(message)s"
        logger_config_custom = Logger(format_string=custom_format)
        self.assertEqual(logger_config_custom.format_string, custom_format)

    def test_get_logger(self) -> None:
        """
        Test getting logger instances.

        Example:
            >>> logger = Logger.get_logger("test")
            >>> logger.name
            'test'
        """
        logger = Logger.get_logger("test_logger")
        self.assertEqual(logger.name, "test_logger")

        debug_logger = Logger.get_logger("debug_logger", level=logging.DEBUG)
        self.assertEqual(debug_logger.level, logging.DEBUG)

    def test_logger_handles_extra_fields(self) -> None:
        """
        Test that logger handles extra fields via formatter.

        Example:
            >>> logger = Logger.get_logger("test")
            >>> logger.info("Test", extra={"key": "value"})
        """
        logger = Logger.get_logger("extra_logger")
        self.assertEqual(logger.name, "extra_logger")
        logger.info("Test message", extra={"test_key": "test_value"})

    def test_logger_with_custom_handlers(self) -> None:
        """Test Logger initialization with custom handlers."""
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        Logger(handlers=[handler])
        self.assertEqual(len(logging.getLogger().handlers), 1)

    def test_logger_with_kwargs(self) -> None:
        """Test Logger initialization with additional kwargs."""
        logger_config = Logger(level=logging.DEBUG, force=True)
        self.assertEqual(logger_config.level, logging.DEBUG)

    def test_get_logger_uses_root_level(self) -> None:
        """Test that get_logger uses root logger level when not specified."""
        Logger(level=logging.WARNING)
        logger = Logger.get_logger("test_root_level")
        self.assertEqual(logger.level, logging.WARNING)

    def test_get_logger_defaults_to_info(self) -> None:
        """Test that get_logger defaults to INFO when root is NOTSET."""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.NOTSET)
        logger = Logger.get_logger("test_default")
        self.assertEqual(logger.level, logging.INFO)

    def test_get_logger_with_root_handlers(self) -> None:
        """Test that get_logger includes root logger's custom handlers."""
        stream = io.StringIO()
        file_handler = logging.StreamHandler(stream)
        Logger(handlers=[file_handler])
        logger = Logger.get_logger("test_with_root_handler")
        # Should have our console handler + the file handler
        self.assertGreaterEqual(len(logger.handlers), 1)

    def test_set_log_format(self) -> None:
        """Test that set_log_format updates the default format for all loggers."""
        Logger()

        # Create logger first to test updating existing handlers
        logger = Logger.get_logger("test_format")
        handler = logger.handlers[0]

        # Add a handler that doesn't match (to cover the False branch)
        other_logger = logging.getLogger("test_other")
        other_handler = logging.StreamHandler()
        other_handler.setFormatter(logging.Formatter("%(message)s"))
        other_logger.addHandler(other_handler)

        # Now change format - should update existing handler with ExtraFieldsFormatter
        # but skip the handler with different formatter
        custom_format = "%(levelname)s: %(message)s"
        Logger.set_log_format(custom_format)

        formatter = handler.formatter
        self.assertIsNotNone(formatter)
        if formatter is not None:
            self.assertEqual(formatter._fmt, custom_format)

        # Verify other handler was not changed
        self.assertIsNotNone(other_handler.formatter)
        if other_handler.formatter is not None:
            self.assertEqual(other_handler.formatter._fmt, "%(message)s")

    def test_set_log_format_reset_to_default(self) -> None:
        """Test that set_log_format resets to default when None is passed."""
        Logger()
        custom_format = "%(levelname)s: %(message)s"
        Logger.set_log_format(custom_format)

        # Reset format to default
        Logger.set_log_format(None, None)

        logger = Logger.get_logger("test_reset")
        handler = logger.handlers[0]
        formatter = handler.formatter

        self.assertIsNotNone(formatter)
        if formatter is not None:
            self.assertEqual(formatter._fmt, Logger.DEFAULT_FORMAT)
            self.assertEqual(formatter.datefmt, Logger.DEFAULT_DATE_FORMAT)

    def test_set_log_format_with_date_format(self) -> None:
        """Test that set_log_format can set date_format separately."""
        Logger()
        custom_date_format = "%Y-%m-%d"
        Logger.set_log_format(None, custom_date_format)

        logger = Logger.get_logger("test_date_format")
        handler = logger.handlers[0]
        formatter = handler.formatter

        self.assertIsNotNone(formatter)
        if formatter is not None:
            self.assertEqual(formatter.datefmt, custom_date_format)

    # ========================================================================
    # LoggerConfig Integration Tests
    # ========================================================================

    def test_get_logger_with_logger_config(self) -> None:
        """Test get_logger() when LoggerConfig is configured."""
        LoggerConfig.configure(prefix="TestApp", level=logging.DEBUG)
        logger = Logger.get_logger("test_logger")
        self.assertEqual(logger.level, logging.DEBUG)
        handler = logger.handlers[0]
        if isinstance(handler.formatter, ExtraFieldsFormatter):
            self.assertEqual(handler.formatter.template_vars.get("prefix"), "TestApp")

    def test_get_logger_without_logger_config(self) -> None:
        """Test get_logger() when LoggerConfig is not configured."""
        logger = Logger.get_logger("test_logger_fallback")
        self.assertIsNotNone(logger)
        self.assertGreater(len(logger.handlers), 0)

    def test_create_handler_with_logger_config(self) -> None:
        """Test _create_handler() uses LoggerConfig formatter when configured."""
        LoggerConfig.configure(prefix="TestApp", format_string="%(message)s")
        handler = Logger._create_handler(logging.INFO)
        self.assertIsInstance(handler.formatter, ExtraFieldsFormatter)

    def test_get_logger_detects_existing_config_handlers(self) -> None:
        """Test get_logger() detects when LoggerConfig handlers already present."""
        handler = logging.StreamHandler(io.StringIO())
        LoggerConfig.configure(prefix="Test", handlers=[handler])
        logger = logging.getLogger("test_existing")
        logger.addHandler(handler)
        logger2 = Logger.get_logger("test_existing")
        self.assertIn(handler, logger2.handlers)

    def test_get_logger_adds_config_handlers_when_not_present(self) -> None:
        """Test get_logger() adds config handlers when not already present."""
        handler = logging.StreamHandler(io.StringIO())
        LoggerConfig.configure(prefix="Test", handlers=[handler])
        logger = Logger.get_logger("test_new")
        self.assertIn(handler, logger.handlers)


if __name__ == "__main__":
    unittest.main()
