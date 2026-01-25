"""
**File:** ``07_handler_management.py``
**Region:** ``ds_common_logger_py_lib``

Description
-----------
Example demonstrating advanced handler management features:
- Adding custom handlers (file, structured logging, etc.)
- Removing handlers
- Setting custom default handlers
- Multiple handlers working together
"""

import json
import logging
import sys
from pathlib import Path

from ds_common_logger_py_lib import Logger

Logger.configure(
    prefix="MyApp",
    format_string="[%(asctime)s][{prefix}][%(name)s][%(levelname)s]: %(message)s",
    level=logging.INFO,
)

# ============================================================================
# Custom Structured JSON Handler
# ============================================================================


class JSONHandler(logging.Handler):
    """
    Custom handler that outputs logs as JSON.

    This demonstrates how to create custom handlers that work with Logger.configure().
    """

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.file = open(file_path, "a")

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record as JSON."""
        log_entry = {
            "timestamp": record.created,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        extra_fields = {
            key: value
            for key, value in record.__dict__.items()
            if key
            not in {
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
        }
        if extra_fields:
            log_entry["extra"] = extra_fields

        self.file.write(json.dumps(log_entry) + "\n")
        self.file.flush()

    def close(self) -> None:
        """Close the file."""
        if self.file:
            self.file.close()
        super().close()


class MyService:
    """Service using Logger.get_logger() - handlers apply automatically."""

    def __init__(self):
        self.logger = Logger.get_logger(f"{__name__}.MyService")

    def do_work(self):
        self.logger.info("Service log message - goes to all configured handlers")
        self.logger.warning("Service warning - goes to all handlers")


def main() -> None:
    log_file = Path("application.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    Logger.add_handler(file_handler)

    logger = Logger.get_logger(__name__)
    logger.info("This message goes to both stdout and application.log")
    logger.warning("Warning messages also go to both")

    json_log_file = Path("application.json.log")
    json_handler = JSONHandler(str(json_log_file))
    json_handler.setLevel(logging.INFO)

    Logger.add_handler(json_handler)

    logger.info(
        "This message goes to stdout, file, and JSON log",
        extra={"user_id": "user_123", "action": "login"},
    )

    logger.info("Before removing JSON handler - goes to all handlers")

    Logger.remove_handler(json_handler)
    json_handler.close()

    logger.info("After removing JSON handler - only goes to stdout and file")

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)

    Logger.set_default_handler(stderr_handler)

    logger.info("Info message - goes to stderr (new default)")
    logger.warning("Warning message - goes to stderr")
    logger.error("Error message - goes to stderr")

    service = MyService()
    service.do_work()

    runtime_log_file = Path("runtime.log")
    runtime_handler = logging.FileHandler(runtime_log_file)
    runtime_handler.setLevel(logging.DEBUG)

    Logger.add_handler(runtime_handler)

    logger.debug("Debug message - goes to runtime.log (and other handlers)")
    logger.info("Info message - goes to all handlers including runtime.log")

    for log_file_path in [log_file, json_log_file, runtime_log_file]:
        if log_file_path.exists():
            log_file_path.unlink()


if __name__ == "__main__":
    main()
