"""
**File:** ``03_log_levels.py``
**Region:** ``ds_common_logger_py_lib``

Description
-----------
This example shows how to control log levels using package-level configuration
from Logger.configure(), with optional runtime overrides per logger.
"""

import logging

from ds_common_logger_py_lib import Logger

Logger.configure(
    level=logging.DEBUG,
    format_string="[%(asctime)s][%(name)s][{prefix}][%(levelname)s][%(filename)s:%(lineno)d]: %(message)s",
    date_format="%Y-%m-%dT%H:%M:%S",
    logger_levels={
        f"{__name__}.VerboseService": logging.DEBUG,
        f"{__name__}.StandardService": logging.INFO,
        f"{__name__}.QuietService": logging.WARNING,
    },
)


class VerboseService:
    """Service with verbose DEBUG logging."""

    def __init__(self):
        self.logger = Logger.get_logger(f"{__name__}.VerboseService")

    def process(self) -> None:
        self.logger.debug("Debug message - only visible with DEBUG level")
        self.logger.info("Info message")
        self.logger.warning("Warning message")


class StandardService:
    """Service with standard INFO logging."""

    def __init__(self):
        self.logger = Logger.get_logger(f"{__name__}.StandardService")

    def process(self) -> None:
        self.logger.debug("Debug message - won't be shown")
        self.logger.info("Info message")
        self.logger.warning("Warning message")


class QuietService:
    """Service with minimal WARNING logging."""

    def __init__(self):
        self.logger = Logger.get_logger(f"{__name__}.QuietService")

    def process(self) -> None:
        self.logger.debug("Debug message - won't be shown")
        self.logger.info("Info message - won't be shown")
        self.logger.warning("Warning message")


class DynamicService:
    """Service that changes log level at runtime."""

    def __init__(self):
        self.logger = Logger.get_logger(f"{__name__}.DynamicService")

    def process(self) -> None:
        self.logger.info("Initial info message")

        self.logger.setLevel(logging.DEBUG)
        self.logger.debug("Now debug messages are visible")

        self.logger.setLevel(logging.WARNING)
        self.logger.info("This info won't be shown")
        self.logger.warning("But warnings will be shown")


if __name__ == "__main__":
    VerboseService().process()
    StandardService().process()
    QuietService().process()
    DynamicService().process()

    main_logger = Logger.get_logger(__name__)
    main_logger.debug("This debug message is visible due to global DEBUG level")
    main_logger.info("Info message")
