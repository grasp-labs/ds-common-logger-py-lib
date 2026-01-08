"""
**File:** ``test_mixin.py``
**Region:** ``ds_common_logger_py_lib``

Description
-----------
Unit tests for ``LoggingMixin``, validating logger naming, caching behavior,
log level overrides, formatting updates, and inheritance interactions.
"""

import logging
import unittest
from unittest import TestCase

from ds_common_logger_py_lib import Logger, LoggingMixin


class TestLoggingMixin(TestCase):
    """Test the LoggingMixin functionality."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        Logger()
        # Clear any existing loggers
        LoggingMixin._loggers.clear()

    def test_mixin_instance_log_property(self) -> None:
        """Test that LoggingMixin provides log property on instances."""

        class TestService(LoggingMixin):
            pass

        service = TestService()
        self.assertIsNotNone(service.log)
        self.assertIsInstance(service.log, logging.Logger)

    def test_mixin_class_logger_method(self) -> None:
        """Test that LoggingMixin provides logger() classmethod."""

        class TestService(LoggingMixin):
            pass

        logger = TestService.logger()
        self.assertIsNotNone(logger)
        self.assertIsInstance(logger, logging.Logger)

    def test_mixin_logger_name_includes_class(self) -> None:
        """Test that logger name includes class name."""

        class UserService(LoggingMixin):
            pass

        service = UserService()
        self.assertIn("UserService", service.log.name)

    def test_mixin_logger_caching(self) -> None:
        """Test that loggers are cached per class."""

        class ServiceA(LoggingMixin):
            pass

        class ServiceB(LoggingMixin):
            pass

        instance_a1 = ServiceA()
        instance_a2 = ServiceA()
        instance_b = ServiceB()

        # Same class should return same logger
        self.assertIs(instance_a1.log, instance_a2.log)
        # Different classes should have different loggers
        self.assertIsNot(instance_a1.log, instance_b.log)

    def test_mixin_with_custom_log_level(self) -> None:
        """Test LoggingMixin with custom log_level class attribute."""

        class DebugService(LoggingMixin):
            log_level = logging.DEBUG

        service = DebugService()
        self.assertEqual(service.log.level, logging.DEBUG)

    def test_mixin_set_log_level(self) -> None:
        """Test set_log_level classmethod."""

        class TestService(LoggingMixin):
            pass

        TestService.set_log_level(logging.DEBUG)
        self.assertEqual(TestService.log_level, logging.DEBUG)

        service = TestService()
        self.assertEqual(service.log.level, logging.DEBUG)

    def test_mixin_set_log_level_updates_existing_logger(self) -> None:
        """Test that set_log_level updates existing logger instance."""

        class TestService(LoggingMixin):
            pass

        # Get logger first
        logger1 = TestService().log
        # Then set level
        TestService.set_log_level(logging.WARNING)
        # Logger should be updated
        self.assertEqual(logger1.level, logging.WARNING)

    def test_mixin_logger_with_level_override(self) -> None:
        """Test logger() method with level override."""

        class TestService(LoggingMixin):
            log_level = logging.INFO

        # Override level in method call
        logger = TestService.logger(level=logging.DEBUG)
        self.assertEqual(logger.level, logging.DEBUG)

    def test_mixin_logger_with_level_override_subsequent_calls(self) -> None:
        """Test that logger() method updates level on subsequent calls."""

        class TestService(LoggingMixin):
            log_level = logging.INFO

        # First call with DEBUG level
        logger1 = TestService.logger(level=logging.DEBUG)
        self.assertEqual(logger1.level, logging.DEBUG)

        # Second call with WARNING level - should update the cached logger
        logger2 = TestService.logger(level=logging.WARNING)
        self.assertIs(logger1, logger2)
        self.assertEqual(logger2.level, logging.WARNING)
        self.assertEqual(logger1.level, logging.WARNING)

        # Third call with ERROR level - should update again
        logger3 = TestService.logger(level=logging.ERROR)
        self.assertIs(logger1, logger3)
        self.assertEqual(logger3.level, logging.ERROR)

    def test_mixin_inheritance(self) -> None:
        """Test LoggingMixin with class inheritance."""

        class BaseService(LoggingMixin):
            pass

        class UserService(BaseService):
            pass

        base = BaseService()
        user = UserService()

        # Each class should have its own logger
        self.assertIsNot(base.log, user.log)
        self.assertIn("BaseService", base.log.name)
        self.assertIn("UserService", user.log.name)

    def test_mixin_inheritance_with_log_level(self) -> None:
        """Test inheritance with log level override."""

        class BaseService(LoggingMixin):
            log_level = logging.INFO

        class DebugService(BaseService):
            log_level = logging.DEBUG

        base = BaseService()
        debug = DebugService()

        self.assertEqual(base.log.level, logging.INFO)
        self.assertEqual(debug.log.level, logging.DEBUG)

    def test_mixin_set_log_format(self) -> None:
        """Test that set_log_format updates the format for all loggers."""

        class TestService(LoggingMixin):
            pass

        custom_format = "%(levelname)s: %(message)s"
        TestService.set_log_format(custom_format)

        service = TestService()
        handler = service.log.handlers[0]
        formatter = handler.formatter

        self.assertIsNotNone(formatter)
        if formatter is not None:
            self.assertEqual(formatter._fmt, custom_format)

    def test_mixin_set_log_format_recreates_existing_logger(self) -> None:
        """Test that set_log_format recreates logger when it already exists."""

        class TestService(LoggingMixin):
            pass

        # Create logger first
        _ = TestService().log
        self.assertIn(TestService, LoggingMixin._loggers)

        # Set format - should delete and recreate logger (line 115 coverage)
        custom_format = "%(levelname)s: %(message)s"
        TestService.set_log_format(custom_format)

        # Verify logger was removed from cache
        self.assertNotIn(TestService, LoggingMixin._loggers)

        # Logger should be recreated with new format
        logger2 = TestService().log
        handler = logger2.handlers[0]
        formatter = handler.formatter

        self.assertIsNotNone(formatter)
        if formatter is not None:
            self.assertEqual(formatter._fmt, custom_format)


if __name__ == "__main__":
    unittest.main()
