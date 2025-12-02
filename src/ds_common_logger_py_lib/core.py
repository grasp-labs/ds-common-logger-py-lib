"""
File: core.py
Description: Core logging functionality for the DS shared logger package.
Region: packages/logging/python

# Example:

from ds_common_logger_py_lib import Logger

Logger()
logger = Logger.get_logger(__name__)
logger.info("Hello, world!")
"""

import logging
import sys
from typing import Any, Optional

from .formatter import ExtraFieldsFormatter


class Logger:
    """
    Logger class for the data pipeline with both instance and static methods.

    Args:
        level: Logging level to set.
        format_string: Optional custom format string.
        **kwargs: Additional arguments passed to logging.basicConfig().
                 Common options include: handlers, force, encoding, errors, style.

    Returns:
        Configured logger instance.

    Example:
        >>> logger_config = Logger(level=logging.DEBUG)
        >>> logger = Logger.get_logger(__name__)
        >>> logger.info("Test message")
        >>> # Custom handlers
        >>> Logger(level=logging.INFO, handlers=[logging.FileHandler("app.log")])
        >>> # Force reconfiguration
        >>> Logger(level=logging.DEBUG, force=True)
    """

    # Default format constants
    DEFAULT_FORMAT = "[%(asctime)s][%(name)s][%(levelname)s][%(filename)s:%(lineno)d]: %(message)s"
    DEFAULT_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

    def __init__(
        self,
        level: int = logging.INFO,
        format_string: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize logger configuration.

        Args:
            level: Logging level to set.
            format_string: Optional custom format string.
            **kwargs: Additional arguments passed to logging.basicConfig().
                     Common options:
                     - handlers: List of handlers (default: StreamHandler to stdout)
                     - force: Force reconfiguration even if already configured
                     - encoding: Encoding for file handlers
                     - errors: Error handling for encoding
                     - style: Format style ('%', '{', or '$')

        Example:
            >>> logger = Logger(level=logging.DEBUG)
            >>> logger.level == logging.DEBUG
            True
            >>> # Use custom handlers
            >>> Logger(handlers=[logging.FileHandler("app.log")])
            >>> # Force reconfiguration
            >>> Logger(level=logging.INFO, force=True)
        """
        self.level = level
        self.format_string = format_string or self.DEFAULT_FORMAT
        self.date_format = self.DEFAULT_DATE_FORMAT
        self._config_kwargs = kwargs
        self._config()

    def _config(self) -> None:
        """
        Configure logging for the entire application.

        Example:
            >>> logger = Logger()
            >>> logger._config()
        """
        config_args: dict[str, Any] = {
            "level": self.level,
            "format": self.format_string,
            "datefmt": self.date_format,
        }

        if "handlers" not in self._config_kwargs:
            config_args["handlers"] = [logging.StreamHandler(sys.stdout)]

        config_args.update(self._config_kwargs)

        logging.basicConfig(**config_args)

    @staticmethod
    def _create_handler(level: int) -> logging.StreamHandler[Any]:
        """
        Create a configured console handler with formatter.

        Args:
            level: Logging level for the handler.

        Returns:
            Configured StreamHandler instance.
        """
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        handler.setFormatter(
            ExtraFieldsFormatter(
                fmt=Logger.DEFAULT_FORMAT,
                datefmt=Logger.DEFAULT_DATE_FORMAT,
            )
        )
        return handler

    @staticmethod
    def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
        """
        Get a configured logger instance.

        Args:
            name: The logger name (usually __name__).
            level: Optional logging level override.

        Returns:
            Configured logger instance.

        Example:
            >>> logger = Logger.get_logger(__name__)
            >>> logger.info("Test message")
        """
        logger = logging.getLogger(name)
        root_logger = logging.getLogger()

        if level is not None:
            effective_level = level
        elif root_logger.level != logging.NOTSET:
            effective_level = root_logger.level
        else:
            effective_level = logging.INFO

        logger.setLevel(effective_level)
        logger.propagate = False

        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        logger.addHandler(Logger._create_handler(effective_level))

        for root_handler in root_logger.handlers:
            if isinstance(root_handler, logging.StreamHandler) and root_handler.stream == sys.stdout:
                continue
            logger.addHandler(root_handler)

        return logger
