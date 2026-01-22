"""
**File:** ``08_application_config.py``
**Region:** ``ds_common_logger_py_lib``

Description
-----------
Example demonstrating application-level configuration using LoggerConfig.

This shows how applications can set their own prefix, format, and handlers
at startup, which will be applied to all loggers created by packages using
Logger.get_logger() or LoggingMixin.
"""

import logging
import sys
from pathlib import Path

from ds_common_logger_py_lib import Logger, LoggerConfig, LoggingMixin


# ============================================================================
# Application Startup Configuration
# ============================================================================

LoggerConfig.configure(
    prefix="MyApp",
    format_string="[%(asctime)s][{prefix}][%(name)s][%(levelname)s]: %(message)s",
    date_format="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
logger = Logger.get_logger(__name__)


class DatabaseService:
    """Simulated database service from a package."""

    def __init__(self):
        self.logger = Logger.get_logger(__name__)

    def connect(self):
        self.logger.info("Connecting to database", extra={"host": "db.example.com"})

    def query(self, sql: str):
        self.logger.debug("Executing query", extra={"sql": sql})
        self.logger.info("Query executed successfully")


class PaymentService(LoggingMixin):
    """Simulated payment service from a package."""

    def process_payment(self, amount: float, user_id: str):
        self.log.info(
            "Processing payment",
            extra={"amount": amount, "user_id": user_id, "currency": "USD"},
        )
        self.log.warning("Payment processed with app prefix included")


if __name__ == "__main__":
    print("=" * 80)
    print("Example 1: Application prefix in log messages")
    print("=" * 80)

    logger.info("This message includes the application prefix")
    logger.warning("Warning messages also include the prefix")

    print("\n" + "=" * 80)
    print("Example 2: Packages using Logger.get_logger() respect app config")
    print("=" * 80)

    db_service = DatabaseService()
    db_service.connect()
    db_service.query("SELECT * FROM users")

    print("\n" + "=" * 80)
    print("Example 3: LoggingMixin also respects app config")
    print("=" * 80)

    payment_service = PaymentService()
    payment_service.process_payment(99.99, "user_123")

    print("\n" + "=" * 80)
    print("Example 4: Custom handlers")
    print("=" * 80)

    log_file = Path("app.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    LoggerConfig.add_handler(file_handler)

    logger.info("This message goes to both stdout and app.log file")
    logger.info("Check app.log to see file logging in action", extra={"file": str(log_file)})

    print(f"\nLog messages also written to: {log_file}")

    print("\n" + "=" * 80)
    print("Example 5: Changing configuration at runtime")
    print("=" * 80)

    LoggerConfig.set_prefix("MyApp-v2")
    LoggerConfig.configure(
        format_string="[{prefix}] %(levelname)s: %(message)s",
        force=True,
    )

    logger.info("After reconfiguration, format changed")
    logger.warning("Prefix is now MyApp-v2")

    print("\n" + "=" * 80)
    print("Example 6: Dynamic prefix updates (e.g., sessionID)")
    print("=" * 80)

    LoggerConfig.configure(
        prefix="MyApp",
        format_string="[%(asctime)s][{prefix}][%(name)s][%(levelname)s]: %(message)s",
        force=True,
    )

    logger.info("Log before session starts")

    session_id = "session_abc123"
    LoggerConfig.set_prefix(f"MyApp-{session_id}")

    logger.info("Log after session starts - includes session ID in prefix")
    logger.warning("All subsequent logs will include the session ID")

    user_id = "user_456"
    LoggerConfig.set_prefix(f"[MyApp][{session_id}][{user_id}]")

    logger.info("Log with updated prefix including user ID")

    print("\n" + "=" * 80)
    print("Example 7: Custom default handler")
    print("=" * 80)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)

    LoggerConfig.set_default_handler(stderr_handler)

    logger.info("Info messages go to stderr now")
    logger.warning("Warning messages also go to stderr")
    logger.error("Error messages go to stderr")

    if log_file.exists():
        log_file.unlink()

    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    print("""
Key benefits of LoggerConfig:

1. Application Control: Applications can set their own prefix and format at startup
2. Package Compatibility: Packages using Logger.get_logger() or LoggingMixin
   automatically get the application's configuration
3. Handler Management: Easy to add/remove handlers for all loggers
4. Template Variables: Use {prefix} in format strings for dynamic prefixes
5. Runtime Updates: Can update prefix at runtime with set_prefix() when context
   changes (e.g., when session starts, user logs in, etc.)

All existing code continues to work - Logger.get_logger() and LoggingMixin
behave identically, but now respect application-level configuration.
""")
