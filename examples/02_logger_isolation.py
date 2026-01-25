"""
**File:** ``02_logger_isolation.py``
**Region:** ``ds_common_logger_py_lib``

Description
-----------
Example script demonstrating why per-class loggers are useful: log filtering by
logger name, per-service level control, and easier source attribution in larger
applications.
"""

import logging

from ds_common_logger_py_lib import Logger

Logger.configure(
    level=logging.DEBUG,
    format_string="[%(asctime)s][%(name)s][{prefix}][%(levelname)s][%(filename)s:%(lineno)d]: %(message)s",
    date_format="%Y-%m-%dT%H:%M:%S",
)


class DatabaseService:
    """Database operations - verbose logging."""

    def __init__(self):
        self.logger = Logger.get_logger(f"{__name__}.DatabaseService")

    def query(self, sql: str) -> list:
        self.logger.debug("Executing query", extra={"sql": sql})
        self.logger.info("Query executed", extra={"rows": 10})
        return [{"id": 1}, {"id": 2}]


class CacheService:
    """Cache operations - minimal logging."""

    def __init__(self):
        self.logger = Logger.get_logger(f"{__name__}.CacheService")

    def get(self, key: str) -> str | None:
        self.logger.debug("Cache lookup", extra={"key": key})
        return "cached_value"

    def set(self, key: str, value: str) -> None:
        self.logger.debug("Cache set", extra={"key": key})


class APIService:
    """API operations - standard logging."""

    def __init__(self):
        self.logger = Logger.get_logger(f"{__name__}.APIService")

    def handle_request(self, endpoint: str) -> dict:
        self.logger.info("Handling request", extra={"endpoint": endpoint})
        return {"status": "ok"}


if __name__ == "__main__":
    db = DatabaseService()
    cache = CacheService()
    api = APIService()

    db.query("SELECT * FROM users")
    cache.get("user:123")
    api.handle_request("/api/users")
