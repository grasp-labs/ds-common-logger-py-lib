"""
**File:** ``core.py``
**Region:** ``ds_common_logger_py_lib``

Description
-----------
Defines the core logging API for this package, including a `Logger` helper for
configuring Python logging, retrieving named loggers, and updating the active
log format across already-created loggers.

Example
-------
    >>> from ds_common_logger_py_lib import Logger
    >>> import logging
    >>>
    >>> Logger()
    >>> logger = Logger.get_logger(__name__)
    >>> record = logging.LogRecord("__main__", logging.INFO, "core.py", 18, "Hello, world!", (), None)
    >>> handler = logger.handlers[0]
    >>> handler.formatter.format(record)
    '[2024-01-15T10:30:45][__main__][INFO][core.py:18]: Hello, world!'
    >>>
    >>> Logger.set_log_format("%(levelname)s: %(message)s")
    >>> record2 = logging.LogRecord("__main__", logging.INFO, "core.py", 22, "Custom format message", (), None)
    >>> handler.formatter.format(record2)
    'INFO: Custom format message'
"""

from __future__ import annotations

import logging
import sys
from typing import Any

from .config import LoggerConfig
from .formatter import ExtraFieldsFormatter


class Logger:
    """
    Logger class for the application with both instance and static methods.

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
        >>> Logger(level=logging.DEBUG)
        >>> logger = Logger.get_logger(__name__)
        >>> record = logging.LogRecord("__main__", logging.INFO, "core.py", 59, "Test message", (), None)
        >>> handler = logger.handlers[0]
        >>> handler.formatter.format(record)
        '[2024-01-15T10:30:45][__main__][INFO][core.py:59]: Test message'
        >>>
        >>> Logger.set_log_format("%(levelname)s: %(message)s")
        >>> record2 = logging.LogRecord("__main__", logging.INFO, "core.py", 63, "Formatted message", (), None)
        >>> handler.formatter.format(record2)
        'INFO: Formatted message'
        >>>
        >>> Logger(level=logging.INFO, handlers=[logging.FileHandler("app.log")])
        >>> Logger(level=logging.DEBUG, force=True)
    """

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
            >>> Logger(level=logging.DEBUG)
            >>> logger = Logger.get_logger(__name__)
            >>> record = logging.LogRecord("__main__", logging.DEBUG, "core.py", 100, "Debug message", (), None)
            >>> handler = logger.handlers[0]
            >>> handler.formatter.format(record)
            '[2024-01-15T10:30:45][__main__][DEBUG][core.py:100]: Debug message'
            >>>
            >>> Logger(handlers=[logging.FileHandler("app.log")])
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
    def _create_handler(level: int) -> logging.Handler:
        """
        Create a configured handler with formatter.

        If LoggerConfig is configured, uses its settings. Otherwise, creates
        a default StreamHandler.

        Args:
            level: Logging level for the handler.

        Returns:
            Configured Handler instance.

        Example:
            >>> handler = Logger._create_handler(logging.INFO)
        """
        if LoggerConfig.is_configured():
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(level)
            handler.setFormatter(LoggerConfig._create_formatter())
            return handler

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
            >>> Logger()
            >>> Logger.set_log_format("%(levelname)s: %(message)s")
            >>> logger = Logger.get_logger(__name__)
            >>> record = logging.LogRecord("__main__", logging.INFO, "core.py", 188, "This will use the custom format", (), None)
            >>> handler = logger.handlers[0]
            >>> handler.formatter.format(record)
            'INFO: This will use the custom format'
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
    def _determine_effective_level(level: int | None, root_logger: logging.Logger) -> int:
        """
        Determine the effective logging level.

        Args:
            level: Optional logging level override. If provided, this takes precedence.
            root_logger: The root logger instance to check for default level.

        Returns:
            The effective logging level to use, determined by priority:
            1. Provided level parameter (if not None)
            2. LoggerConfig level (if LoggerConfig is configured)
            3. Root logger level (if set)
            4. Default INFO level
        """
        if level is not None:
            return level
        if LoggerConfig.is_configured():
            return LoggerConfig._level
        if root_logger.level != logging.NOTSET:
            return root_logger.level
        return logging.INFO

    @staticmethod
    def _has_handler(logger: logging.Logger) -> bool:
        """
        Check if logger has appropriate handlers.

        Args:
            logger: The logger instance to check for handlers.

        Returns:
            True if the logger has appropriate handlers configured, False otherwise.
            When LoggerConfig is configured, checks for any handlers or LoggerConfig handlers.
            Otherwise, checks for handlers with ExtraFieldsFormatter.
        """
        if LoggerConfig.is_configured():
            if len(logger.handlers) > 0:
                return True
            config_handler_ids = {id(h) for h in LoggerConfig._handlers}
            if LoggerConfig._default_handler:
                config_handler_ids.add(id(LoggerConfig._default_handler))
            existing_handler_ids = {id(h) for h in logger.handlers}
            return bool(config_handler_ids & existing_handler_ids)
        return any(
            isinstance(h.formatter, ExtraFieldsFormatter)
            for h in logger.handlers
            if isinstance(h, logging.StreamHandler) and h.formatter
        )

    @staticmethod
    def _add_handlers_to_logger(logger: logging.Logger, effective_level: int) -> None:
        """
        Add handlers to logger if needed.

        Creates a default handler and adds it to the logger. If LoggerConfig is
        configured, also adds any additional handlers from LoggerConfig, avoiding
        duplicates.

        Args:
            logger: The logger instance to add handlers to.
            effective_level: The logging level to set on the handlers.
        """
        handler = Logger._create_handler(effective_level)
        logger.addHandler(handler)

        if LoggerConfig.is_configured():
            existing_handler_ids = {id(h) for h in logger.handlers}
            for config_handler in LoggerConfig._handlers:
                if id(config_handler) not in existing_handler_ids:
                    logger.addHandler(config_handler)
                    existing_handler_ids.add(id(config_handler))

    @staticmethod
    def _apply_formatter_to_logger(logger: logging.Logger, effective_level: int) -> None:
        """
        Apply formatter to all handlers if LoggerConfig is configured.

        Updates all handlers on the logger with the current LoggerConfig formatter
        and sets their logging level. If LoggerConfig is not configured, this
        method does nothing.

        Args:
            logger: The logger instance whose handlers should be updated.
            effective_level: The logging level to set on all handlers.
        """
        if LoggerConfig.is_configured():
            formatter = LoggerConfig._create_formatter()
            for handler in logger.handlers:
                handler.setFormatter(formatter)
                handler.setLevel(effective_level)

    @staticmethod
    def get_logger(
        name: str,
        level: int | None = None,
    ) -> logging.Logger:
        """
        Get a configured logger instance.

        If LoggerConfig is configured, the logger will use application-level
        settings (prefix, format, handlers). Otherwise, uses default settings.

        Args:
            name: The logger name (usually __name__).
            level: Optional logging level override.

        Returns:
            Configured logger instance.

        Example:
            >>> Logger()
            >>> logger = Logger.get_logger(__name__)
            >>> record = logging.LogRecord("__main__", logging.INFO, "core.py", 232, "Test message", (), None)
            >>> handler = logger.handlers[0]
            >>> handler.formatter.format(record)
            '[2024-01-15T10:30:45][__main__][INFO][core.py:232]: Test message'
        """
        logger = logging.getLogger(name)
        root_logger = logging.getLogger()

        effective_level = Logger._determine_effective_level(level, root_logger)
        logger.setLevel(effective_level)
        logger.propagate = False

        if not Logger._has_handler(logger):
            Logger._add_handlers_to_logger(logger, effective_level)

        Logger._apply_formatter_to_logger(logger, effective_level)

        return logger
