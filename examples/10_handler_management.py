"""
**File:** ``10_handler_management.py``
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

from ds_common_logger_py_lib import Logger, LoggerConfig, LoggingMixin


# ============================================================================
# Custom Structured JSON Handler
# ============================================================================


class JSONHandler(logging.Handler):
    """
    Custom handler that outputs logs as JSON.

    This demonstrates how to create custom handlers that work with LoggerConfig.
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


class MyService(LoggingMixin):
    """Service using LoggingMixin - handlers apply automatically."""

    def do_work(self):
        self.log.info("Service log message - goes to all configured handlers")
        self.log.warning("Service warning - goes to all handlers")


if __name__ == "__main__":
    # ============================================================================
    # Example 1: Basic Handler Management
    # ============================================================================

    print("=" * 80)
    print("Example 1: Adding File Handler")
    print("=" * 80)

    LoggerConfig.configure(
        prefix="MyApp",
        format_string="[%(asctime)s][{prefix}][%(name)s][%(levelname)s]: %(message)s",
        level=logging.INFO,
    )

    log_file = Path("application.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    LoggerConfig.add_handler(file_handler)

    logger = Logger.get_logger(__name__)
    logger.info("This message goes to both stdout and application.log")
    logger.warning("Warning messages also go to both")

    print(f"Check {log_file} to see file logging")

    # ============================================================================
    # Example 2: Multiple Handlers
    # ============================================================================

    print("\n" + "=" * 80)
    print("Example 2: Multiple Handlers (stdout + file + JSON)")
    print("=" * 80)

    json_log_file = Path("application.json.log")
    json_handler = JSONHandler(str(json_log_file))
    json_handler.setLevel(logging.INFO)

    LoggerConfig.add_handler(json_handler)

    logger.info(
        "This message goes to stdout, file, and JSON log",
        extra={"user_id": "user_123", "action": "login"},
    )

    print(f"Check {json_log_file} to see JSON structured logs")

    # ============================================================================
    # Example 3: Removing Handlers
    # ============================================================================

    print("\n" + "=" * 80)
    print("Example 3: Removing a Handler")
    print("=" * 80)

    logger.info("Before removing JSON handler - goes to all handlers")

    LoggerConfig.remove_handler(json_handler)
    json_handler.close()

    logger.info("After removing JSON handler - only goes to stdout and file")

    # ============================================================================
    # Example 4: Custom Default Handler
    # ============================================================================

    print("\n" + "=" * 80)
    print("Example 4: Custom Default Handler (stderr for errors)")
    print("=" * 80)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)

    LoggerConfig.set_default_handler(stderr_handler)

    logger.info("Info message - goes to stderr (new default)")
    logger.warning("Warning message - goes to stderr")
    logger.error("Error message - goes to stderr")

    # ============================================================================
    # Example 5: Handler Management with LoggingMixin
    # ============================================================================

    print("\n" + "=" * 80)
    print("Example 5: Handlers Work with LoggingMixin")
    print("=" * 80)

    service = MyService()
    service.do_work()

    # ============================================================================
    # Example 6: Runtime Handler Updates
    # ============================================================================

    print("\n" + "=" * 80)
    print("Example 6: Adding Handler at Runtime")
    print("=" * 80)

    runtime_log_file = Path("runtime.log")
    runtime_handler = logging.FileHandler(runtime_log_file)
    runtime_handler.setLevel(logging.DEBUG)

    LoggerConfig.add_handler(runtime_handler)

    logger.debug("Debug message - goes to runtime.log (and other handlers)")
    logger.info("Info message - goes to all handlers including runtime.log")

    print(f"Check {runtime_log_file} to see runtime-added handler logs")

    # ============================================================================
    # Cleanup
    # ============================================================================

    for log_file_path in [log_file, json_log_file, runtime_log_file]:
        if log_file_path.exists():
            log_file_path.unlink()

    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    print("""
Handler Management Features:

1. add_handler(): Add handlers that apply to all loggers (existing and future)
2. remove_handler(): Remove handlers from all loggers
3. set_default_handler(): Replace the default handler for all loggers
4. Multiple handlers: Can have multiple handlers (stdout, file, JSON, etc.)
5. Automatic application: Handlers automatically apply to Logger.get_logger()
   and LoggingMixin loggers
6. Runtime updates: Can add/remove handlers at runtime

All handler management operations affect all loggers created via
Logger.get_logger() or LoggingMixin, giving applications full control
over where and how logs are written.
""")
