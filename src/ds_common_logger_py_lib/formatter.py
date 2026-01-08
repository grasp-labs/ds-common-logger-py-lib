"""
**File:** ``formatter.py``
**Region:** ``ds_common_logger_py_lib``

Description
-----------
Defines a custom logging formatter that appends non-standard LogRecord fields
(i.e. values passed via the ``extra=...`` argument) to the formatted log output.

Example
-------
.. code-block:: python

    import logging

    from ds_common_logger_py_lib.formatter import ExtraFieldsFormatter

    formatter = ExtraFieldsFormatter()
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger("test")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    logger.info("Test message", extra={"user_id": 123})
"""

import json
import logging
from typing import ClassVar


class ExtraFieldsFormatter(logging.Formatter):
    """
    Custom formatter that includes extra fields in log output.

    This formatter extends the standard logging.Formatter to properly handle
    extra fields passed via the extra parameter in logging calls. Extra fields
    are serialized as JSON and appended to the log message.

    Args:
        fmt: Format string for the log message.
        datefmt: Date format string.

    Returns:
        Formatter instance that handles extra fields.

    Example:
        >>> formatter = ExtraFieldsFormatter()
        >>> handler = logging.StreamHandler()
        >>> handler.setFormatter(formatter)
        >>> logger = logging.getLogger("test")
        >>> logger.addHandler(handler)
        >>> logger.info("Test message", extra={"user_id": 123})
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

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record, including extra fields.

        Args:
            record: The LogRecord instance to format.

        Returns:
            Formatted log message string with extra fields appended if present.

        Example:
            >>> formatter = ExtraFieldsFormatter()
            >>> record = logging.LogRecord("test", logging.INFO, "test.py", 1, "Test", (), None)
            >>> record.user_id = 123
            >>> formatted = formatter.format(record)
            >>> "user_id" in formatted
            True
        """
        msg = super().format(record)

        extra_fields = {key: value for key, value in record.__dict__.items() if key not in self._STANDARD_ATTRS}

        if extra_fields:
            try:
                extra_str = json.dumps(extra_fields, default=str)
                msg = f"{msg} | extra: {extra_str}"
            except (TypeError, ValueError):
                msg = f"{msg} | extra: {extra_fields}"

        return msg
