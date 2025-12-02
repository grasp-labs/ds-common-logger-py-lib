"""
File: test_core.py
Description: Test the core Logger functionality for the DS shared logger package.
Region: packages/logging/python/tests

# Example:

from ds_common_logger_py_lib import Logger

logger = Logger.get_logger(__name__)
logger.info("Test message", extra={"key": "value"})
"""

import io
import logging
import unittest
from unittest import TestCase

from ds_common_logger_py_lib import Logger


class TestLogging(TestCase):
    """
    Test the logging functionality.

    Example:
        >>> test = TestLogging()
        >>> test.test_logging_with_extra()
    """

    def setUp(self) -> None:
        """Set up test fixtures."""
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


if __name__ == "__main__":
    unittest.main()
