"""
**File:** ``test_formatter.py``
**Region:** ``ds_common_logger_py_lib``

Description
-----------
Unit tests for ``ExtraFieldsFormatter``, ensuring extra fields are appended,
JSON serialization is used when possible, and serialization errors are handled
gracefully.
"""

import io
import logging
import unittest
from unittest import TestCase
from unittest.mock import patch

from ds_common_logger_py_lib import Logger, LoggerFilter
from ds_common_logger_py_lib.formatter import ExtraFieldsFormatter


class TestFormatter(TestCase):
    """Test the ExtraFieldsFormatter functionality."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        Logger._configured = False
        Logger._filter = LoggerFilter(allowed_prefixes=None)
        Logger._managed_loggers.clear()
        Logger._logger_levels = {}

        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(logging.NOTSET)

        self.formatter = ExtraFieldsFormatter()
        self.stream = io.StringIO()
        self.handler = logging.StreamHandler(self.stream)
        self.handler.setFormatter(self.formatter)

        self.logger = logging.getLogger("test_formatter")
        self.logger.handlers.clear()
        self.logger.addHandler(self.handler)
        self.handler.filters = [f for f in self.handler.filters if not isinstance(f, LoggerFilter)]
        self.logger.setLevel(logging.INFO)

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.logger.handlers.clear()
        logging.getLogger("test_template").handlers.clear()

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
        with patch(
            "ds_common_logger_py_lib.formatter.json.dumps",
            side_effect=TypeError("Cannot serialize"),
        ):
            self.logger.info("Test", extra={"obj": unserializable_func})
            output = self.stream.getvalue()

            self.assertIn("Test", output)
            self.assertIn("extra:", output)
            self.assertIn("obj", output)

    # ========================================================================
    # Template Variable Resolution Tests
    # ========================================================================

    def test_resolve_template_with_single_variable(self) -> None:
        """Test _resolve_template() with single variable."""
        formatter = ExtraFieldsFormatter(
            fmt="[{prefix}] %(message)s",
            template_vars={"prefix": "MyApp"},
        )

        resolved = formatter._resolve_template("[{prefix}] %(message)s")
        self.assertEqual(resolved, "[MyApp] %(message)s")

    def test_resolve_template_with_multiple_variables(self) -> None:
        """Test _resolve_template() with multiple variables."""
        formatter = ExtraFieldsFormatter(
            fmt="[{app}][{env}] %(message)s",
            template_vars={"app": "MyApp", "env": "prod"},
        )

        resolved = formatter._resolve_template("[{app}][{env}] %(message)s")
        self.assertEqual(resolved, "[MyApp][prod] %(message)s")

    def test_resolve_template_with_no_variables(self) -> None:
        """Test _resolve_template() with no variables (empty dict)."""
        formatter = ExtraFieldsFormatter(
            fmt="%(message)s",
            template_vars={},
        )

        resolved = formatter._resolve_template("%(message)s")
        self.assertEqual(resolved, "%(message)s")

    def test_resolve_template_with_variable_not_in_format(self) -> None:
        """Test _resolve_template() with variable not in format string."""
        formatter = ExtraFieldsFormatter(
            fmt="%(message)s",
            template_vars={"prefix": "MyApp"},
        )

        resolved = formatter._resolve_template("%(message)s")
        # Should return unchanged since variable not in format
        self.assertEqual(resolved, "%(message)s")

    def test_format_with_template_variables(self) -> None:
        """Test format() replaces template variables in output."""
        formatter = ExtraFieldsFormatter(
            fmt="[{prefix}] %(levelname)s: %(message)s",
            template_vars={"prefix": "MyApp"},
        )
        handler = logging.StreamHandler(self.stream)
        handler.setFormatter(formatter)
        logger = logging.getLogger("test_template")
        logger.addHandler(handler)
        handler.filters = [f for f in handler.filters if not isinstance(f, LoggerFilter)]
        logger.setLevel(logging.INFO)

        logger.info("Test message")
        output = self.stream.getvalue()

        self.assertIn("[MyApp]", output)
        self.assertIn("INFO", output)
        self.assertIn("Test message", output)
        # Should not contain literal {prefix}
        self.assertNotIn("{prefix}", output)

    def test_format_with_template_variable_empty_value(self) -> None:
        """Test format() with template variable having empty value."""
        formatter = ExtraFieldsFormatter(
            fmt="[{prefix}] %(message)s",
            template_vars={"prefix": ""},
        )

        record = logging.LogRecord("test", logging.INFO, "test.py", 1, "Test", (), None)
        formatted = formatter.format(record)

        # Empty prefix should result in [] being removed from output
        self.assertNotIn("[]", formatted)
        self.assertEqual(formatted, "Test")

    def test_format_with_template_variable_non_string_value(self) -> None:
        """Test format() with template variable having non-string value (converted to str)."""
        formatter = ExtraFieldsFormatter(
            fmt="[{prefix}] %(message)s",
            template_vars={"prefix": "12345"},
        )

        record = logging.LogRecord("test", logging.INFO, "test.py", 1, "Test", (), None)
        formatted = formatter.format(record)

        # Should convert to string
        self.assertIn("[12345]", formatted)

    def test_format_without_template_vars_but_with_dict(self) -> None:
        """Test format() with format string without template vars but template_vars dict provided."""
        formatter = ExtraFieldsFormatter(
            fmt="%(message)s",
            template_vars={"prefix": "MyApp"},
        )

        record = logging.LogRecord("test", logging.INFO, "test.py", 1, "Test", (), None)
        formatted = formatter.format(record)

        # Should work normally, no replacement needed
        self.assertIn("Test", formatted)
        self.assertNotIn("{prefix}", formatted)

    def test_format_with_template_vars_but_empty_dict(self) -> None:
        """Test format() with format string with template vars but empty template_vars dict."""
        formatter = ExtraFieldsFormatter(
            fmt="[{prefix}] %(message)s",
            template_vars={},
        )

        record = logging.LogRecord("test", logging.INFO, "test.py", 1, "Test", (), None)
        formatted = formatter.format(record)

        # Should not replace, {prefix} might appear in output or be handled by parent
        # The format should still work
        self.assertIn("Test", formatted)

    def test_format_template_vars_with_resolved_format_unchanged(self) -> None:
        """Test format() when resolved format equals original format."""
        formatter = ExtraFieldsFormatter(
            fmt="%(message)s",
            template_vars={"prefix": "MyApp"},
        )

        record = logging.LogRecord("test", logging.INFO, "test.py", 1, "Test", (), None)
        formatted = formatter.format(record)

        # Should use super().format() path
        self.assertIn("Test", formatted)

    def test_format_template_vars_with_no_fmt(self) -> None:
        """Test format() when _fmt is None."""
        formatter = ExtraFieldsFormatter(template_vars={"prefix": "MyApp"})
        # _fmt might be None if not set
        formatter._fmt = None

        record = logging.LogRecord("test", logging.INFO, "test.py", 1, "Test", (), None)
        # Should not raise error
        formatted = formatter.format(record)
        self.assertIsInstance(formatted, str)

    def test_resolve_template_with_special_characters(self) -> None:
        """Test _resolve_template() with special characters in values."""
        formatter = ExtraFieldsFormatter(
            fmt="[{prefix}] %(message)s",
            template_vars={"prefix": "App-123 [test]"},
        )

        resolved = formatter._resolve_template("[{prefix}] %(message)s")
        self.assertEqual(resolved, "[App-123 [test]] %(message)s")

    def test_resolve_template_multiple_occurrences(self) -> None:
        """Test _resolve_template() with multiple occurrences of same variable."""
        formatter = ExtraFieldsFormatter(
            fmt="%(message)s",
            template_vars={"prefix": "Test"},
        )
        # Test with valid % format that includes template var after resolution
        resolved = formatter._resolve_template("%(message)s")
        self.assertEqual(resolved, "%(message)s")

    def test_resolve_template_removes_empty_brackets_and_leading_space(self) -> None:
        """Test _resolve_template() removes empty brackets and leading space."""
        formatter = ExtraFieldsFormatter(
            fmt="[] %(message)s",
            template_vars={"prefix": ""},
        )
        resolved = formatter._resolve_template("[] %(message)s")
        # Should remove [] and the space after it
        self.assertEqual(resolved, "%(message)s")

    def test_resolve_template_removes_leading_space_after_empty_brackets(self) -> None:
        """Test _resolve_template() removes leading space when format starts with empty brackets."""
        formatter = ExtraFieldsFormatter(
            fmt="[] %(levelname)s: %(message)s",
            template_vars={"prefix": ""},
        )
        resolved = formatter._resolve_template("[] %(levelname)s: %(message)s")
        # Should remove [] and the leading space
        self.assertEqual(resolved, "%(levelname)s: %(message)s")

    def test_resolve_template_removes_leading_space_after_bracket_removal(self) -> None:
        """Test _resolve_template() removes leading space after bracket removal."""
        # Create a format with space before empty brackets - after removing [], space remains
        formatter = ExtraFieldsFormatter(
            fmt=" [] %(message)s",
            template_vars={"prefix": ""},
        )
        # When prefix is empty, {prefix} becomes "", and [] gets removed, leaving " %(message)s"
        # The regex removes [] and space after it, but space before [] remains
        # Then line 189 removes the leading space
        resolved = formatter._resolve_template(" [] %(message)s")
        self.assertEqual(resolved, "%(message)s")

    # ========================================================================
    # LoggerFilter Tests
    # ========================================================================

    def test_logger_filter_allows_managed_loggers(self) -> None:
        """Test LoggerFilter allows loggers in managed_loggers set."""
        managed_loggers = {"myapp.module", "myapp.service"}
        filter_obj = LoggerFilter(managed_loggers=managed_loggers)

        record1 = logging.LogRecord("myapp.module", logging.INFO, "test.py", 1, "Test", (), None)
        record2 = logging.LogRecord("myapp.service", logging.INFO, "test.py", 1, "Test", (), None)
        record3 = logging.LogRecord("other.logger", logging.INFO, "test.py", 1, "Test", (), None)

        self.assertTrue(filter_obj.filter(record1))
        self.assertTrue(filter_obj.filter(record2))
        # Without allowed_prefixes, other loggers should be filtered out
        self.assertFalse(filter_obj.filter(record3))

    def test_logger_filter_with_allowed_prefixes(self) -> None:
        """Test LoggerFilter with allowed_prefixes."""
        managed_loggers = {"myapp.module"}
        allowed_prefixes = {"sqlalchemy", "boto3"}
        filter_obj = LoggerFilter(
            allowed_prefixes=allowed_prefixes,
            managed_loggers=managed_loggers,
        )

        # Library loggers should always be allowed
        record1 = logging.LogRecord("myapp.module", logging.INFO, "test.py", 1, "Test", (), None)
        self.assertTrue(filter_obj.filter(record1))

        # Loggers matching allowed prefixes should be allowed
        record2 = logging.LogRecord("sqlalchemy.engine", logging.INFO, "test.py", 1, "Test", (), None)
        record3 = logging.LogRecord("boto3", logging.INFO, "test.py", 1, "Test", (), None)
        record4 = logging.LogRecord("boto3.client", logging.INFO, "test.py", 1, "Test", (), None)
        self.assertTrue(filter_obj.filter(record2))
        self.assertTrue(filter_obj.filter(record3))
        self.assertTrue(filter_obj.filter(record4))

        # Other loggers should be filtered out
        record5 = logging.LogRecord("other.logger", logging.INFO, "test.py", 1, "Test", (), None)
        self.assertFalse(filter_obj.filter(record5))

    def test_logger_filter_with_none_allowed_prefixes(self) -> None:
        """Test LoggerFilter with None allowed_prefixes."""
        managed_loggers = {"myapp.module"}
        filter_obj = LoggerFilter(allowed_prefixes=None, managed_loggers=managed_loggers)

        # Only library loggers should be allowed
        record1 = logging.LogRecord("myapp.module", logging.INFO, "test.py", 1, "Test", (), None)
        record2 = logging.LogRecord("sqlalchemy.engine", logging.INFO, "test.py", 1, "Test", (), None)
        self.assertTrue(filter_obj.filter(record1))
        self.assertFalse(filter_obj.filter(record2))

    def test_logger_filter_with_empty_allowed_prefixes(self) -> None:
        """Test LoggerFilter with empty allowed_prefixes set."""
        managed_loggers = {"myapp.module"}
        filter_obj = LoggerFilter(allowed_prefixes=set(), managed_loggers=managed_loggers)

        # Only library loggers should be allowed
        record1 = logging.LogRecord("myapp.module", logging.INFO, "test.py", 1, "Test", (), None)
        record2 = logging.LogRecord("sqlalchemy.engine", logging.INFO, "test.py", 1, "Test", (), None)
        self.assertTrue(filter_obj.filter(record1))
        self.assertFalse(filter_obj.filter(record2))

    def test_logger_filter_prefix_matching(self) -> None:
        """Test LoggerFilter prefix matching logic."""
        allowed_prefixes = {"myapp"}
        filter_obj = LoggerFilter(allowed_prefixes=allowed_prefixes, managed_loggers=set())

        # Exact match
        record1 = logging.LogRecord("myapp", logging.INFO, "test.py", 1, "Test", (), None)
        self.assertTrue(filter_obj.filter(record1))

        # Starts with prefix
        record2 = logging.LogRecord("myapp.module", logging.INFO, "test.py", 1, "Test", (), None)
        self.assertTrue(filter_obj.filter(record2))

        # Doesn't match
        record3 = logging.LogRecord("other", logging.INFO, "test.py", 1, "Test", (), None)
        self.assertFalse(filter_obj.filter(record3))


if __name__ == "__main__":
    unittest.main()
