"""
Example: Logger isolation and filtering benefits.

Demonstrates how per-class loggers enable:
- Filtering logs by class/service
- Setting different log levels per class
- Identifying log sources in complex applications
"""

from ds_common_logger_py_lib import LoggingMixin


class DatabaseService(LoggingMixin):
    """Database operations - verbose logging."""

    def query(self, sql: str) -> list:
        self.log.debug("Executing query", extra={"sql": sql})
        self.log.info("Query executed", extra={"rows": 10})
        return [{"id": 1}, {"id": 2}]


class CacheService(LoggingMixin):
    """Cache operations - minimal logging."""

    def get(self, key: str) -> str | None:
        self.log.debug("Cache lookup", extra={"key": key})
        return "cached_value"

    def set(self, key: str, value: str) -> None:
        self.log.debug("Cache set", extra={"key": key})


class APIService(LoggingMixin):
    """API operations - standard logging."""

    def handle_request(self, endpoint: str) -> dict:
        self.log.info("Handling request", extra={"endpoint": endpoint})
        return {"status": "ok"}


if __name__ == "__main__":
    """
    In production, you can filter logs by logger name:
    - Only see DatabaseService logs: filter by "examples.03_logger_isolation.DatabaseService"
    - Only see errors: filter by level
    - Track specific service: filter by logger name pattern
    """
    db = DatabaseService()
    cache = CacheService()
    api = APIService()

    # All services log simultaneously
    # Each log line shows which class/service it came from
    db.query("SELECT * FROM users")
    cache.get("user:123")
    api.handle_request("/api/users")
