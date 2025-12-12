"""
File: core.py
Description: Core logging functionality for the DS shared logger package.
Region: packages/logging/python

# Example:

from ds_common_logger_py_lib import Logger

Logger()
logger = Logger.get_logger(__name__)
logger.info("Hello, world!")

# Customize default format
Logger.set_log_format("%(levelname)s: %(message)s")
logger.info("Custom format message")
"""

from __future__ import annotations

import logging
import sys
from typing import Any

from .formatter import ExtraFieldsFormatter


class Logger:
    """
    Logger class for the data pipeline with both instance and static methods.

    The default format can be customized by calling set_log_format() or by
    passing a format_string to __init__().

    Args:
        level: Logging level to set.
        format_string: Optional custom format string. If provided, updates the
                      active format used by all loggers created via get_logger().
        **kwargs: Additional arguments passed to logging.basicConfig().
                 Common options include: handlers, force, encoding, errors, style.

    Returns:
        Configured logger instance.

    Example:
        >>> logger_config = Logger(level=logging.DEBUG)
        >>> logger = Logger.get_logger(__name__)
        >>> logger.info("Test message")
        >>> # Custom format for all loggers
        >>> Logger.set_log_format("%(levelname)s: %(message)s")
        >>> logger = Logger.get_logger(__name__)
        >>> # Custom handlers
        >>> Logger(level=logging.INFO, handlers=[logging.FileHandler("app.log")])
        >>> # Force reconfiguration
        >>> Logger(level=logging.DEBUG, force=True)
    """

    # Default format constants
    DEFAULT_FORMAT = "[%(asctime)s][%(name)s][%(levelname)s][%(filename)s:%(lineno)d]: %(message)s"
    DEFAULT_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

    _active_format: str = DEFAULT_FORMAT
    _active_date_format: str = DEFAULT_DATE_FORMAT

    def __init__(
        self,
        level: int = logging.INFO,
        format_string: str | None = None,
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

        if format_string is not None:
            Logger._active_format = format_string
            Logger._active_date_format = self.date_format

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

        Example:
            >>> handler = Logger._create_handler(logging.INFO)
        """
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        handler.setFormatter(
            ExtraFieldsFormatter(
                fmt=Logger._active_format,
                datefmt=Logger._active_date_format,
            )
        )
        return handler

    @staticmethod
    def set_log_format(
        format_string: str | None = None,
        date_format: str | None = None,
    ) -> None:
        """
        Set or update the default log format for all loggers.

        Args:
            format_string: Format string to set. If None, resets to DEFAULT_FORMAT.
            date_format: Date format string to set. If None, resets to DEFAULT_DATE_FORMAT.

        Example:
            >>> Logger.set_log_format("%(levelname)s: %(message)s")
            >>> logger = Logger.get_logger(__name__)
            >>> logger.info("This will use the custom format")
        """
        if format_string is not None:
            Logger._active_format = format_string
        else:
            Logger._active_format = Logger.DEFAULT_FORMAT

        if date_format is not None:
            Logger._active_date_format = date_format
        else:
            Logger._active_date_format = Logger.DEFAULT_DATE_FORMAT

        for logger_name in logging.Logger.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            for handler in logger.handlers:
                if isinstance(handler, logging.StreamHandler) and isinstance(handler.formatter, ExtraFieldsFormatter):
                    handler.setFormatter(
                        ExtraFieldsFormatter(
                            fmt=Logger._active_format,
                            datefmt=Logger._active_date_format,
                        )
                    )

    @staticmethod
    def get_logger(
        name: str,
        level: int | None = None,
    ) -> logging.Logger:
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

        has_handler = any(
            isinstance(h.formatter, ExtraFieldsFormatter)
            for h in logger.handlers
            if isinstance(h, logging.StreamHandler) and h.formatter
        )

        if not has_handler:
            logger.addHandler(Logger._create_handler(effective_level))

        return logger
