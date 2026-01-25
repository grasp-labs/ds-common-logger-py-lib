"""
**File:** ``05_application_config.py``
**Region:** ``ds_common_logger_py_lib``

Description
-----------
Example demonstrating application-level configuration using Logger.configure(),
including package-level log overrides for internal modules.

This shows how applications can set their own prefix, format, and handlers
at startup, which will be applied to all loggers created by packages using
Logger.get_logger().
"""

import logging
import sys
from pathlib import Path

from ds_common_logger_py_lib import Logger

Logger.configure(
    prefix="MyApp",
    format_string="[%(asctime)s][{prefix}][%(name)s][%(levelname)s]: %(message)s",
    date_format="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
    logger_levels={
        f"{__name__}.DatabaseService": logging.WARNING,
        f"{__name__}.PaymentService": logging.INFO,
    },
)
logger = Logger.get_logger(__name__)


class DatabaseService:
    """Simulated database service from a package."""

    def __init__(self) -> None:
        self.logger = Logger.get_logger(f"{__name__}.DatabaseService")

    def connect(self):
        self.logger.info("Connecting to database", extra={"host": "db.example.com"})

    def query(self, sql: str):
        self.logger.debug("Executing query", extra={"sql": sql})
        self.logger.info("Query executed successfully")


class PaymentService:
    """Simulated payment service from a package."""

    def __init__(self) -> None:
        self.logger = Logger.get_logger(f"{__name__}.PaymentService")

    def process_payment(self, amount: float, user_id: str):
        self.logger.info(
            "Processing payment",
            extra={"amount": amount, "user_id": user_id, "currency": "USD"},
        )
        self.logger.warning("Payment processed with app prefix included")


def main() -> None:
    logger.info("This message includes the application prefix")
    logger.warning("Warning messages also include the prefix")

    db_service = DatabaseService()
    db_service.connect()
    db_service.query("SELECT * FROM users")

    payment_service = PaymentService()
    payment_service.process_payment(99.99, "user_123")

    log_file = Path("app.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    Logger.add_handler(file_handler)

    logger.info("This message goes to both stdout and app.log file")
    logger.info("Check app.log to see file logging in action", extra={"file": str(log_file)})

    Logger.set_prefix("MyApp-v2")
    Logger.configure(
        format_string="[{prefix}] %(levelname)s: %(message)s",
        force=True,
    )

    logger.info("After reconfiguration, format changed")
    logger.warning("Prefix is now MyApp-v2")

    Logger.configure(
        prefix="MyApp",
        format_string="[%(asctime)s][{prefix}][%(name)s][%(levelname)s]: %(message)s",
        force=True,
    )

    logger.info("Log before session starts")

    session_id = "session_abc123"
    Logger.set_prefix(f"MyApp-{session_id}")

    logger.info("Log after session starts - includes session ID in prefix")
    logger.warning("All subsequent logs will include the session ID")

    user_id = "user_456"
    Logger.set_prefix(f"[MyApp][{session_id}][{user_id}]")

    logger.info("Log with updated prefix including user ID")

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)

    Logger.set_default_handler(stderr_handler)

    logger.info("Info messages go to stderr now")
    logger.warning("Warning messages also go to stderr")
    logger.error("Error messages go to stderr")

    if log_file.exists():
        log_file.unlink()


if __name__ == "__main__":
    main()
