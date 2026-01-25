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

from ds_common_logger_py_lib import Logger
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
        # Reset Logger
        Logger._configured = False
        Logger._prefix = ""
        Logger._format_string = None
        Logger._date_format = None
        Logger._level = logging.INFO
        Logger._handlers = []
        Logger._default_handler = None
        Logger._managed_loggers.clear()
        Logger._logger_levels = {}

        # Reset root logger to clean state
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(logging.NOTSET)

    def test_logging_with_extra(self) -> None:
        """
        Test that logging with extra fields works correctly.

        Example:
            >>> Logger.configure()
            >>> logger = Logger.get_logger(__name__)
            >>> logger.info("Test", extra={"key": "value"})
        """
        Logger.configure()
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
        Test logger configuration with different parameters.

        Example:
            >>> Logger.configure(level=logging.DEBUG)
        """
        Logger.configure(level=logging.INFO)
        self.assertEqual(Logger._level, logging.INFO)

        Logger.configure(level=logging.DEBUG, force=True)
        self.assertEqual(Logger._level, logging.DEBUG)

        custom_format = "%(name)s - %(message)s"
        Logger.configure(format_string=custom_format, force=True)
        self.assertEqual(Logger._format_string, custom_format)

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

        debug_logger = Logger.get_logger("debug_logger")
        debug_logger.setLevel(logging.DEBUG)
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
        """Test Logger configuration with custom handlers."""
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        Logger.configure(handlers=[handler])
        self.assertEqual(len(logging.getLogger().handlers), 1)

    def test_logger_with_force(self) -> None:
        """Test Logger configuration with force parameter."""
        Logger.configure(level=logging.DEBUG, force=True)
        self.assertEqual(Logger._level, logging.DEBUG)

    def test_get_logger_uses_configured_level(self) -> None:
        """Test that get_logger inherits configured level from root logger."""
        Logger.configure(level=logging.WARNING)
        logger = Logger.get_logger("test_root_level")
        self.assertEqual(logger.level, logging.NOTSET)
        self.assertEqual(logger.getEffectiveLevel(), logging.WARNING)

    def test_get_logger_defaults_to_info(self) -> None:
        """Test that get_logger inherits from root when root is NOTSET."""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.NOTSET)
        logger = Logger.get_logger("test_default")
        self.assertEqual(logger.level, logging.NOTSET)
        self.assertEqual(logger.getEffectiveLevel(), logging.NOTSET)

    def test_get_logger_uses_root_level_when_not_configured(self) -> None:
        """Test that get_logger inherits root logger level when Logger not configured."""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.WARNING)
        logger = Logger.get_logger("test_root_level_not_configured")
        self.assertEqual(logger.level, logging.NOTSET)
        self.assertEqual(logger.getEffectiveLevel(), logging.WARNING)

    def test_get_logger_with_root_handlers(self) -> None:
        """Test that get_logger includes root logger's custom handlers."""
        stream = io.StringIO()
        file_handler = logging.StreamHandler(stream)
        Logger.configure(handlers=[file_handler])
        logger = Logger.get_logger("test_with_root_handler")
        self.assertEqual(logger.propagate, True)

    def test_get_logger_with_package_normalization(self) -> None:
        """Test get_logger(package=True) normalizes internal package names."""
        logger = Logger.get_logger("ds_common_serde_py_lib.encoder", package=True)
        self.assertEqual(logger.name, "ds.common.serde.py.lib.encoder")

    def test_logger_levels_apply_to_new_loggers(self) -> None:
        """Test logger-level rules apply when creating new loggers."""
        Logger.configure(
            logger_levels={
                "myapp": logging.WARNING,
                "myapp.service": logging.ERROR,
            },
        )

        service_logger = Logger.get_logger("myapp.service.api")
        base_logger = Logger.get_logger("myapp.utils")
        other_logger = Logger.get_logger("other")

        self.assertEqual(service_logger.level, logging.NOTSET)
        self.assertEqual(service_logger.getEffectiveLevel(), logging.ERROR)
        self.assertEqual(base_logger.level, logging.NOTSET)
        self.assertEqual(base_logger.getEffectiveLevel(), logging.WARNING)
        self.assertEqual(other_logger.level, logging.NOTSET)

    def test_logger_levels_apply_to_existing_loggers(self) -> None:
        """Test logger-level rules apply to loggers created earlier."""
        existing_logger = Logger.get_logger("myapp.existing")
        self.assertEqual(existing_logger.level, logging.NOTSET)

        Logger.configure(logger_levels={"myapp": logging.INFO})

        self.assertEqual(existing_logger.level, logging.NOTSET)
        self.assertEqual(existing_logger.getEffectiveLevel(), logging.INFO)

    def test_set_log_format(self) -> None:
        """Test that set_log_format updates the default format for all loggers."""
        Logger.configure()

        _ = Logger.get_logger("test_format")
        root_logger = logging.getLogger()
        handler = root_logger.handlers[0] if root_logger.handlers else None
        self.assertIsNotNone(handler)

        other_logger = logging.getLogger("test_other")
        other_handler = logging.StreamHandler()
        other_handler.setFormatter(logging.Formatter("%(message)s"))
        other_logger.addHandler(other_handler)

        custom_format = "%(levelname)s: %(message)s"
        Logger.set_log_format(custom_format)

        if handler is not None:
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
        Logger.configure()
        custom_format = "%(levelname)s: %(message)s"
        Logger.set_log_format(custom_format)
        Logger.set_log_format(None, None)

        root_logger = logging.getLogger()
        handler = root_logger.handlers[0] if root_logger.handlers else None
        self.assertIsNotNone(handler)
        if handler is not None:
            formatter = handler.formatter
            self.assertIsNotNone(formatter)
            if formatter is not None:
                self.assertEqual(formatter._fmt, Logger.DEFAULT_FORMAT)
                self.assertEqual(formatter.datefmt, Logger.DEFAULT_DATE_FORMAT)

    def test_set_log_format_with_date_format(self) -> None:
        """Test that set_log_format can set date_format separately."""
        Logger.configure()
        custom_date_format = "%Y-%m-%d"
        Logger.set_log_format(None, custom_date_format)

        root_logger = logging.getLogger()
        handler = root_logger.handlers[0] if root_logger.handlers else None
        self.assertIsNotNone(handler)
        if handler is not None:
            formatter = handler.formatter
            self.assertIsNotNone(formatter)
            if formatter is not None:
                self.assertEqual(formatter.datefmt, custom_date_format)

    # ========================================================================
    # Logger Configuration Integration Tests
    # ========================================================================

    def test_get_logger_with_logger_config(self) -> None:
        """Test get_logger() when Logger.configure() is called."""
        Logger.configure(prefix="TestApp", level=logging.DEBUG)
        logger = Logger.get_logger("test_logger")
        self.assertEqual(logger.level, logging.NOTSET)
        self.assertEqual(logger.getEffectiveLevel(), logging.DEBUG)
        root_logger = logging.getLogger()
        self.assertGreater(len(root_logger.handlers), 0)
        handler = root_logger.handlers[0]
        if isinstance(handler.formatter, ExtraFieldsFormatter):
            self.assertEqual(handler.formatter.template_vars.get("prefix"), "TestApp")

    def test_get_logger_without_logger_config(self) -> None:
        """Test get_logger() when Logger.configure() is not called."""
        logger = Logger.get_logger("test_logger_fallback")
        self.assertIsNotNone(logger)

    def test_get_logger_detects_existing_config_handlers(self) -> None:
        """Test get_logger() works with configured handlers on root logger."""
        handler = logging.StreamHandler(io.StringIO())
        Logger.configure(prefix="Test", handlers=[handler])
        logger = Logger.get_logger("test_existing")
        self.assertEqual(logger.propagate, True)

    def test_get_logger_uses_root_handlers(self) -> None:
        """Test get_logger() uses root logger handlers via propagation."""
        handler = logging.StreamHandler(io.StringIO())
        Logger.configure(prefix="Test", handlers=[handler])
        logger = Logger.get_logger("test_new")
        root_logger = logging.getLogger()
        self.assertIn(handler, root_logger.handlers)
        self.assertEqual(logger.propagate, True)

    def test_remove_handler_when_not_configured(self) -> None:
        """Test remove_handler() returns early when not configured."""
        handler = logging.StreamHandler(io.StringIO())
        Logger.remove_handler(handler)

    def test_get_managed_loggers(self) -> None:
        """Test get_managed_loggers() returns the set of managed loggers."""
        Logger._managed_loggers.clear()
        _ = Logger.get_logger("test_logger_1")
        _ = Logger.get_logger("test_logger_2")
        managed_loggers = Logger.get_managed_loggers()
        self.assertIn("test_logger_1", managed_loggers)
        self.assertIn("test_logger_2", managed_loggers)


if __name__ == "__main__":
    unittest.main()
