"""
**File:** ``config.py``
**Region:** ``ds_common_logger_py_lib``

Description
-----------
Defines the ``LoggerConfig`` class for application-level logger configuration.
"""

from __future__ import annotations

import logging
import sys
from typing import ClassVar

from .formatter import ExtraFieldsFormatter

DEFAULT_FORMAT = "[%(asctime)s][%(name)s][%(levelname)s][%(filename)s:%(lineno)d]: %(message)s"
DEFAULT_FORMAT_WITH_PREFIX = "[%(asctime)s][{prefix}][%(name)s][%(levelname)s][%(filename)s:%(lineno)d]: %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


class LoggerConfig:
    """
    Application-level logger configuration manager.

    This class allows applications to configure logging at startup with their own
    prefix, format, and handlers. Configuration set via LoggerConfig takes precedence
    over package-level Logger() calls.

    Example:
        >>> from ds_common_logger_py_lib import LoggerConfig, Logger
        >>> import logging
        >>>
        >>> LoggerConfig.configure(
        ...     prefix="MyApp",
        ...     format_string="[%(asctime)s][{prefix}][%(name)s][%(levelname)s]: %(message)s",
        ...     level=logging.INFO
        ... )
        >>> logger = Logger.get_logger(__name__)
        >>> record = logging.LogRecord("__main__", logging.INFO, "config.py", 41, "Application started", (), None)
        >>> handler = logger.handlers[0]
        >>> handler.formatter.format(record)
        '[2024-01-15T10:30:45][MyApp][__main__][INFO]: Application started'
        >>>
        >>> LoggerConfig.set_prefix("MyApp-session123")
        >>> record2 = logging.LogRecord("__main__", logging.INFO, "config.py", 45, "Session initialized", (), None)
        >>> handler.formatter.format(record2)
        '[2024-01-15T10:30:46][MyApp-session123][__main__][INFO]: Session initialized'
    """

    _configured: bool = False
    _prefix: str = ""
    _format_string: str = DEFAULT_FORMAT_WITH_PREFIX
    _date_format: str = DEFAULT_DATE_FORMAT
    _level: int = logging.INFO
    _handlers: ClassVar[list[logging.Handler]] = []
    _default_handler: logging.Handler | None = None

    @classmethod
    def configure(
        cls,
        prefix: str = "",
        format_string: str = DEFAULT_FORMAT_WITH_PREFIX,
        date_format: str = DEFAULT_DATE_FORMAT,
        level: int = logging.INFO,
        handlers: list[logging.Handler] | None = None,
        default_handler: logging.Handler | None = None,
        force: bool = False,
    ) -> None:
        """
        Configure application-level logging settings.

        This should be called once at application startup, before any packages
        start using the logger. The configuration will be applied to all loggers
        created via Logger.get_logger().

        Args:
            prefix: Prefix to inject into log messages (via {prefix} in format).
                   Can be updated later with set_prefix().
            format_string: Format string for log messages. Uses {prefix} to include the prefix.
                          Uses DEFAULT_FORMAT_WITH_PREFIX by default.
            date_format: Date format string. Uses DEFAULT_DATE_FORMAT by default.
            level: Default logging level.
            handlers: List of handlers to add to all loggers. If None, uses default StreamHandler.
            default_handler: Single default handler to use for all loggers. If provided,
                           this replaces the default StreamHandler.
            force: If True, force reconfiguration even if already configured.

        Example:
            >>> from ds_common_logger_py_lib import LoggerConfig, Logger
            >>> import logging
            >>> LoggerConfig.configure(
            ...     prefix="MyService",
            ...     format_string="[%(asctime)s][{prefix}][%(name)s]: %(message)s",
            ...     level=logging.DEBUG
            ... )
            >>> logger = Logger.get_logger(__name__)
            >>> record = logging.LogRecord("__main__", logging.INFO, "config.py", 94, "Service started", (), None)
            >>> handler = logger.handlers[0]
            >>> handler.formatter.format(record)
            '[2024-01-15T10:30:45][MyService][__main__]: Service started'
        """
        if cls._configured and not force:
            return

        was_configured = cls._configured
        cls._configured = True

        if not was_configured or prefix:
            cls._prefix = prefix

        if format_string is not None:
            cls._format_string = format_string
        if date_format is not None:
            cls._date_format = date_format

        cls._level = level

        if default_handler is not None:
            cls._default_handler = default_handler
        elif handlers is not None:
            cls._handlers = list(handlers)
            cls._default_handler = None
        else:
            cls._default_handler = logging.StreamHandler(sys.stdout)
            cls._default_handler.setLevel(level)
            cls._handlers = []

        root_logger = logging.getLogger()
        root_logger.setLevel(level)

        if force:
            root_logger.handlers.clear()

        if cls._default_handler:
            root_logger.addHandler(cls._default_handler)
        else:
            for handler in cls._handlers:
                root_logger.addHandler(handler)

        cls._update_existing_loggers()

    @classmethod
    def set_prefix(cls, prefix: str) -> None:
        """
        Update the prefix at runtime.

        This allows you to change the prefix dynamically, for example when a
        session starts or when context changes. The new prefix will be applied
        to all existing and future loggers.

        If LoggerConfig hasn't been configured yet, this will automatically
        configure it with default settings that include {prefix} in the format
        (using the provided prefix).

        Args:
            prefix: New prefix value to use in log messages.

        Example:
            >>> from ds_common_logger_py_lib import LoggerConfig, Logger
            >>> import logging
            >>> LoggerConfig.set_prefix("MyApp")
            >>> logger = Logger.get_logger(__name__)
            >>> record = logging.LogRecord("__main__", logging.INFO, "config.py", 158, "Log with MyApp prefix", (), None)
            >>> handler = logger.handlers[0]
            >>> handler.formatter.format(record)
            '[2024-01-15T10:30:45][MyApp][__main__][INFO][config.py:158]: Log with MyApp prefix'
            >>>
            >>> session_id = "session_12345"
            >>> LoggerConfig.set_prefix(f"[{session_id}]")
            >>> record2 = logging.LogRecord("__main__", logging.INFO, "config.py", 162, "Log with session prefix", (), None)
            >>> handler.formatter.format(record2)
            '[2024-01-15T10:30:46][session_12345][__main__][INFO][config.py:162]: Log with session prefix'
        """
        if not cls._configured:
            cls.configure(prefix=prefix, format_string=DEFAULT_FORMAT_WITH_PREFIX)

        cls._prefix = prefix
        cls._update_existing_loggers()

    @classmethod
    def add_handler(cls, handler: logging.Handler) -> None:
        """
        Add a handler to all existing and future loggers.

        Args:
            handler: Handler to add.

        Example:
            >>> from ds_common_logger_py_lib import LoggerConfig, Logger
            >>> import logging
            >>> LoggerConfig.configure()
            >>> file_handler = logging.FileHandler("app.log")
            >>> LoggerConfig.add_handler(file_handler)
            >>> logger = Logger.get_logger(__name__)
            >>> len(logger.handlers) > 1
            True
        """
        if not cls._configured:
            raise RuntimeError("LoggerConfig must be configured before adding handlers")

        cls._handlers.append(handler)
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)

        for logger_name in logging.Logger.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            if logger is not root_logger:
                logger.addHandler(handler)

    @classmethod
    def remove_handler(cls, handler: logging.Handler) -> None:
        """
        Remove a handler from all loggers.

        Args:
            handler: Handler to remove.

        Example:
            >>> from ds_common_logger_py_lib import LoggerConfig, Logger
            >>> import logging
            >>> LoggerConfig.configure()
            >>> file_handler = logging.FileHandler("app.log")
            >>> LoggerConfig.add_handler(file_handler)
            >>> logger = Logger.get_logger(__name__)
            >>> file_handler in logger.handlers
            True
            >>> LoggerConfig.remove_handler(file_handler)
            >>> file_handler in logger.handlers
            False
        """
        if not cls._configured:
            return

        if handler in cls._handlers:
            cls._handlers.remove(handler)

        root_logger = logging.getLogger()
        if handler in root_logger.handlers:
            root_logger.removeHandler(handler)

        for logger_name in logging.Logger.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            if handler in logger.handlers:
                logger.removeHandler(handler)

    @classmethod
    def set_default_handler(cls, handler: logging.Handler) -> None:
        """
        Set the default handler for all loggers, replacing the current default.

        Args:
            handler: Handler to use as default.

        Example:
            >>> from ds_common_logger_py_lib import LoggerConfig, Logger
            >>> import logging
            >>> import sys
            >>> LoggerConfig.configure()
            >>> custom_handler = logging.StreamHandler(sys.stderr)
            >>> LoggerConfig.set_default_handler(custom_handler)
            >>> logger = Logger.get_logger(__name__)
            >>> custom_handler in logger.handlers
            True
        """
        if not cls._configured:
            raise RuntimeError("LoggerConfig must be configured before setting default handler")

        if cls._default_handler:
            cls.remove_handler(cls._default_handler)

        cls._default_handler = handler
        handler.setLevel(cls._level)

        formatter = cls._create_formatter()
        handler.setFormatter(formatter)

        root_logger = logging.getLogger()
        root_logger.addHandler(handler)

        for logger_name in logging.Logger.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            if logger is not root_logger and not logger.handlers:
                logger.addHandler(handler)

    @classmethod
    def _create_formatter(cls) -> ExtraFieldsFormatter:
        """Create a formatter with current configuration."""
        format_string = cls._format_string or DEFAULT_FORMAT
        date_format = cls._date_format or DEFAULT_DATE_FORMAT

        template_vars = {}
        if cls._prefix:
            template_vars["prefix"] = cls._prefix

        return ExtraFieldsFormatter(
            fmt=format_string,
            datefmt=date_format,
            template_vars=template_vars,
        )

    @classmethod
    def _update_existing_loggers(cls) -> None:
        """Update all existing loggers with current configuration."""
        formatter = cls._create_formatter()

        for logger_name in logging.Logger.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            logger.setLevel(cls._level)

            for handler in logger.handlers:
                handler.setFormatter(formatter)
                handler.setLevel(cls._level)

    @classmethod
    def is_configured(cls) -> bool:
        """Check if LoggerConfig has been configured."""
        return cls._configured

    @classmethod
    def get_prefix(cls) -> str:
        """Get the configured prefix."""
        return cls._prefix

    @classmethod
    def get_format_string(cls) -> str | None:
        """Get the configured format string."""
        return cls._format_string

    @classmethod
    def get_date_format(cls) -> str | None:
        """Get the configured date format."""
        return cls._date_format
