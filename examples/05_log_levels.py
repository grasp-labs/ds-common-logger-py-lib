"""
**File:** ``05_log_levels.py``
**Region:** ``ds_common_logger_py_lib``

Description
-----------
Example script showing how to control log levels with ``LoggingMixin`` using
class defaults, runtime updates, and per-call overrides.
"""

from ds_common_logger_py_lib import LoggingMixin, LoggerConfig
import logging

LoggerConfig.configure(
    level=logging.DEBUG,
    format_string="[%(asctime)s][%(name)s][{prefix}][%(levelname)s][%(filename)s:%(lineno)d]: %(message)s",
    date_format="%Y-%m-%dT%H:%M:%S",
)


class VerboseService(LoggingMixin):
    """Service with verbose DEBUG logging."""

    log_level = logging.DEBUG

    def process(self) -> None:
        self.log.debug("Debug message - only visible with DEBUG level")
        self.log.info("Info message")
        self.log.warning("Warning message")


class StandardService(LoggingMixin):
    """Service with standard INFO logging."""

    log_level = logging.INFO

    def process(self) -> None:
        self.log.debug("Debug message - won't be shown")
        self.log.info("Info message")
        self.log.warning("Warning message")


class QuietService(LoggingMixin):
    """Service with minimal WARNING logging."""

    log_level = logging.WARNING

    def process(self) -> None:
        self.log.debug("Debug message - won't be shown")
        self.log.info("Info message - won't be shown")
        self.log.warning("Warning message")


class DynamicService(LoggingMixin):
    """Service that changes log level at runtime."""

    def process(self) -> None:
        self.log.info("Initial info message")

        # Change log level dynamically
        self.__class__.set_log_level(logging.DEBUG)
        self.log.debug("Now debug messages are visible")

        # Change back to WARNING
        self.__class__.set_log_level(logging.WARNING)
        self.log.info("This info won't be shown")
        self.log.warning("But warnings will be shown")


if __name__ == "__main__":
    print("=== VerboseService (DEBUG level) ===")
    VerboseService().process()

    print("\n=== StandardService (INFO level) ===")
    StandardService().process()

    print("\n=== QuietService (WARNING level) ===")
    QuietService().process()

    print("\n=== DynamicService (changing levels) ===")
    DynamicService().process()

    print("\n=== Override level per call ===")
    # Override level for a specific call
    logger = StandardService.logger(level=logging.DEBUG)
    logger.debug("This debug message is visible due to override")
    logger.info("Info message")
