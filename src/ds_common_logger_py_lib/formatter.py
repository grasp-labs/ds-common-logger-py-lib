"""
**File:** ``formatter.py``
**Region:** ``ds_common_logger_py_lib``

Description
-----------
Defines a custom logging formatter that appends non-standard LogRecord fields
(i.e. values passed via the ``extra=...`` argument) to the formatted log output.

Example
-------
    >>> import logging
    >>> from ds_common_logger_py_lib.formatter import ExtraFieldsFormatter
    >>>
    >>> formatter = ExtraFieldsFormatter()
    >>> handler = logging.StreamHandler()
    >>> handler.setFormatter(formatter)
    >>>
    >>> logger = logging.getLogger("test")
    >>> logger.addHandler(handler)
    >>> logger.setLevel(logging.INFO)
    >>>
    >>> logger.info("Test message", extra={"user_id": 123})
    [2024-01-15T10:30:45][test][INFO][formatter.py:26]: Test message | extra: {"user_id": 123}
"""

import json
import logging
import re
from typing import ClassVar


class ExtraFieldsFormatter(logging.Formatter):
    """
    Custom formatter that includes extra fields in log output.

    This formatter extends the standard logging.Formatter to properly handle
    extra fields passed via the extra parameter in logging calls. Extra fields
    are serialized as JSON and appended to the log message.

    The formatter also supports template variables in format strings, such as
    {app_prefix}, which are replaced at runtime with values from the LoggerConfig.

    Args:
        fmt: Format string for the log message. May contain template variables
             like {app_prefix} that will be replaced at runtime.
        datefmt: Date format string.
        template_vars: Optional dictionary of template variables to replace in
                     the format string (e.g., {"app_prefix": "MyApp"}).

    Returns:
        Formatter instance that handles extra fields and template variables.

    Example:
        >>> import logging
        >>> formatter = ExtraFieldsFormatter(
        ...     fmt="[%(asctime)s][{prefix}][%(name)s]: %(message)s",
        ...     template_vars={"prefix": "MyApp"}
        ... )
        >>> handler = logging.StreamHandler()
        >>> handler.setFormatter(formatter)
        >>> logger = logging.getLogger("test")
        >>> logger.addHandler(handler)
        >>> logger.setLevel(logging.INFO)
        >>> logger.info("Test message", extra={"user_id": 123})
        [2024-01-15T10:30:45][MyApp][test]: Test message | extra: {"user_id": 123}
    """

    _STANDARD_ATTRS: ClassVar[set[str]] = {
        "name",
        "msg",
        "args",
        "created",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "module",
        "msecs",
        "message",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "thread",
        "threadName",
        "exc_info",
        "exc_text",
        "stack_info",
        "taskName",
        "asctime",
    }

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        template_vars: dict[str, str] | None = None,
    ) -> None:
        """
        Initialize the formatter with optional template variables.

        Args:
            fmt: Format string for the log message.
            datefmt: Date format string.
            template_vars: Optional dictionary of template variables to replace.
        """
        super().__init__(fmt, datefmt)
        self.template_vars = template_vars or {}
        self._resolved_fmt: str | None = None

    def _resolve_template(self, fmt: str) -> str:
        """
        Resolve template variables in the format string.
        Remove empty bracket pairs: [] and optional space after it
        This handles patterns like "[] " or "[]" at the start/middle/end of format string

        Args:
            fmt: Format string with potential template variables.

        Returns:
            Format string with template variables replaced.
        """
        if not self.template_vars:
            return fmt

        resolved = fmt
        for key, value in self.template_vars.items():
            resolved = resolved.replace(f"{{{key}}}", str(value))

        resolved = re.sub(r"\[\]\s*", "", resolved)
        resolved = re.sub(r"  +", " ", resolved)
        if resolved.startswith(" "):
            resolved = resolved[1:]
        return resolved

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record, including extra fields.

        Args:
            record: The LogRecord instance to format.

        Returns:
            Formatted log message string with extra fields appended if present.

        Example:
            >>> import logging
            >>> formatter = ExtraFieldsFormatter()
            >>> handler = logging.StreamHandler()
            >>> handler.setFormatter(formatter)
            >>> logger = logging.getLogger("test")
            >>> logger.addHandler(handler)
            >>> logger.setLevel(logging.INFO)
            >>> logger.info("Test", extra={"user_id": 123})
            [2024-01-15T10:30:45][test][INFO][test.py:1]: Test | extra: {"user_id": 123}
        """
        if self.template_vars and self._fmt:
            resolved_fmt = self._resolve_template(self._fmt)
            if resolved_fmt != self._fmt:
                temp_formatter = logging.Formatter(resolved_fmt, self.datefmt)
                msg = temp_formatter.format(record)
            else:
                msg = super().format(record)
        else:
            msg = super().format(record)

        extra_fields = {key: value for key, value in record.__dict__.items() if key not in self._STANDARD_ATTRS}

        if extra_fields:
            try:
                extra_str = json.dumps(extra_fields, default=str)
                msg = f"{msg} | extra: {extra_str}"
            except (TypeError, ValueError):
                msg = f"{msg} | extra: {extra_fields}"

        return msg
