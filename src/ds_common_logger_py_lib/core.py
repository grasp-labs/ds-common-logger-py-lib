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
    >>> Logger.configure()
    >>> logger = Logger.get_logger(__name__)
    >>> logger.info("Hello, world!")
    [2024-01-15T10:30:45][__main__][INFO][core.py:18]: Hello, world!
    >>>
    >>> Logger.set_log_format("%(levelname)s: %(message)s")
    >>> logger.info("Custom format message")
    INFO: Custom format message
"""

from __future__ import annotations

import logging
import sys
from typing import ClassVar

from .formatter import ExtraFieldsFormatter, LoggerFilter


class Logger:
    """
    Logger class for the application with static methods only.

    Configure the logger using Logger.configure() before using Logger.get_logger().
    The default format can be customized by calling set_log_format() or by
    passing a format_string to configure().

    Example:
        >>> Logger.configure(level=logging.DEBUG)
        >>> logger = Logger.get_logger(__name__)
        >>> logger.info("Test message")
        [2024-01-15T10:30:45][__main__][INFO][core.py:59]: Test message
        >>>
        >>> Logger.set_log_format("%(levelname)s: %(message)s")
        >>> logger.info("Formatted message")
        INFO: Formatted message
        >>>
        >>> Logger.configure(level=logging.INFO, handlers=[logging.FileHandler("app.log")])
        >>> Logger.configure(level=logging.DEBUG, force=True)
    """

    DEFAULT_FORMAT = "[%(asctime)s][%(name)s][%(levelname)s][%(filename)s:%(lineno)d]: %(message)s"
    DEFAULT_FORMAT_WITH_PREFIX = "[%(asctime)s][{prefix}][%(name)s][%(levelname)s][%(filename)s:%(lineno)d]: %(message)s"
    DEFAULT_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

    _configured: bool = False
    _prefix: str = ""
    _format_string: str | None = DEFAULT_FORMAT_WITH_PREFIX
    _date_format: str | None = DEFAULT_DATE_FORMAT
    _level: int = logging.INFO
    _handlers: ClassVar[list[logging.Handler]] = []
    _default_handler: logging.Handler | None = None
    _managed_loggers: ClassVar[set[str]] = set()
    _logger_levels: ClassVar[dict[str, int]] = {}
    _filter: LoggerFilter = LoggerFilter(managed_loggers=_managed_loggers)

    @staticmethod
    def configure(
        prefix: str = "",
        format_string: str = DEFAULT_FORMAT_WITH_PREFIX,
        date_format: str = DEFAULT_DATE_FORMAT,
        level: int = logging.INFO,
        handlers: list[logging.Handler] | None = None,
        default_handler: logging.Handler | None = None,
        allowed_prefixes: set[str] | None = None,
        logger_levels: dict[str, int] | None = None,
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
            allowed_prefixes: Set of logger name prefixes to allow in addition to
                            library-created loggers. Default is None, which means only
                            loggers created via Logger.get_logger() are allowed.
                            To include third-party library logs, add their prefixes:
                            {"sqlalchemy", "boto3"} to see SQLAlchemy and boto3 logs.
            logger_levels: Optional mapping of logger names to logging levels.
                           If provided, levels are applied to the parent loggers for
                           those names (e.g., setting "myapp" sets the parent logger
                           for "myapp.*"). Pass an empty dict to clear existing rules.
            force: If True, force reconfiguration even if already configured.

        Example:
            >>> from ds_common_logger_py_lib import Logger
            >>> import logging
            >>> Logger.configure(
            ...     prefix="MyService",
            ...     format_string="[%(asctime)s][{prefix}][%(name)s]: %(message)s",
            ...     level=logging.DEBUG
            ...     logger_levels={
            ...         "ds": logging.WARNING,
            ...     },
            ... )
            >>> logger = Logger.get_logger(__name__)
            >>> logger.info("Service started")
            [2024-01-15T10:30:45][MyService][__main__]: Service started
        """
        if Logger._configured and not force:
            return

        was_configured = Logger._configured
        Logger._configured = True

        if not was_configured or prefix:
            Logger._prefix = prefix

        Logger._format_string = format_string
        Logger._date_format = date_format

        Logger._level = level
        Logger._filter = LoggerFilter(
            allowed_prefixes=allowed_prefixes,
            managed_loggers=Logger._managed_loggers,
        )

        previous_logger_levels: dict[str, int] | None = None
        if logger_levels is not None:
            previous_logger_levels = dict(Logger._logger_levels)
            Logger._logger_levels = dict(logger_levels)

        if default_handler is not None:
            Logger._default_handler = default_handler
        elif handlers is not None:
            Logger._handlers = list(handlers)
            Logger._default_handler = None
        else:
            Logger._default_handler = logging.StreamHandler(sys.stdout)
            Logger._default_handler.setLevel(level)
            Logger._handlers = []

        Logger._setup_filter()

        root_logger = logging.getLogger()
        root_logger.setLevel(level)

        if force:
            root_logger.handlers.clear()

        formatter = Logger._create_formatter()
        if Logger._default_handler:
            Logger._default_handler.setFormatter(formatter)
            root_logger.addHandler(Logger._default_handler)
        else:
            for handler in Logger._handlers:
                handler.setFormatter(formatter)
                root_logger.addHandler(handler)

        Logger._update_existing_loggers()
        Logger._apply_logger_levels(previous_logger_levels)

    @staticmethod
    def get_logger(
        name: str,
        package: bool = False,
    ) -> logging.Logger:
        """
        Get a configured logger instance.

        If Logger.configure() is called, the logger will use application-level
        settings (prefix, format, handlers). Otherwise, uses default settings.

        Args:
            name: The logger name (usually __name__).
            package: If True, normalize internal package names into a shared
                     namespace (e.g., ds_common_* -> ds.common.*).

        Returns:
            Configured logger instance.

        Example:
            >>> Logger.configure()
            >>> logger = Logger.get_logger(__name__)
            >>> logger.info("Test message")
            [2024-01-15T10:30:45][__main__][INFO][core.py:232]: Test message
        """
        logger_name = Logger._normalize_logger_name(name) if package else name
        logger = logging.getLogger(logger_name)
        Logger._register_managed_logger(logger_name)
        logger.propagate = True
        return logger

    @staticmethod
    def set_prefix(prefix: str) -> None:
        """
        Update the prefix at runtime.

        This allows you to change the prefix dynamically, for example when a
        session starts or when context changes. The new prefix will be applied
        to all existing and future loggers.

        If Logger.configure() hasn't been called yet, this will automatically
        configure it with default settings that include {prefix} in the format
        (using the provided prefix).

        Args:
            prefix: New prefix value to use in log messages.

        Example:
            >>> from ds_common_logger_py_lib import Logger
            >>> import logging
            >>> Logger.set_prefix("MyApp")
            >>> logger = Logger.get_logger(__name__)
            >>> logger.info("Log with MyApp prefix")
            [2024-01-15T10:30:45][MyApp][__main__][INFO][core.py:158]: Log with MyApp prefix
            >>>
            >>> session_id = "session_12345"
            >>> Logger.set_prefix(f"[{session_id}]")
            >>> logger.info("Log with session prefix")
            [2024-01-15T10:30:46][session_12345][__main__][INFO][core.py:162]: Log with session prefix
        """
        if not Logger._configured:
            Logger.configure(prefix=prefix, format_string=Logger.DEFAULT_FORMAT_WITH_PREFIX)

        Logger._prefix = prefix
        Logger._update_existing_loggers()

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
            >>> Logger.configure()
            >>> Logger.set_log_format("%(levelname)s: %(message)s")
            >>> logger = Logger.get_logger(__name__)
            >>> logger.info("This will use the custom format")
            INFO: This will use the custom format
        """
        if format_string is not None:
            Logger._format_string = format_string
        else:
            Logger._format_string = Logger.DEFAULT_FORMAT

        if date_format is not None:
            Logger._date_format = date_format
        else:
            Logger._date_format = Logger.DEFAULT_DATE_FORMAT

        # Update root logger handlers only (child loggers propagate to root)
        root_logger = logging.getLogger()
        formatter = Logger._create_formatter()
        for handler in root_logger.handlers:
            if isinstance(handler.formatter, ExtraFieldsFormatter):
                handler.setFormatter(formatter)

    @staticmethod
    def add_handler(handler: logging.Handler) -> None:
        """
        Add a handler to the root logger.

        When Logger.configure() is called, handlers are on the root logger only.
        Package loggers propagate to root, so they will use this handler automatically.

        Args:
            handler: Handler to add.

        Example:
            >>> from ds_common_logger_py_lib import Logger
            >>> import logging
            >>> Logger.configure()
            >>> file_handler = logging.FileHandler("app.log")
            >>> Logger.add_handler(file_handler)
            >>> logger = Logger.get_logger(__name__)
            >>> logger.info("Message goes to file via root logger")
        """
        if not Logger._configured:
            raise RuntimeError("Logger must be configured before adding handlers")

        handler.addFilter(Logger._filter)
        handler.setFormatter(Logger._create_formatter())
        Logger._handlers.append(handler)
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)

    @staticmethod
    def remove_handler(handler: logging.Handler) -> None:
        """
        Remove a handler from the root logger.

        Args:
            handler: Handler to remove.

        Example:
            >>> from ds_common_logger_py_lib import Logger
            >>> import logging
            >>> Logger.configure()
            >>> file_handler = logging.FileHandler("app.log")
            >>> Logger.add_handler(file_handler)
            >>> Logger.remove_handler(file_handler)
        """
        if not Logger._configured:
            return

        if handler in Logger._handlers:
            Logger._handlers.remove(handler)

        root_logger = logging.getLogger()
        if handler in root_logger.handlers:
            root_logger.removeHandler(handler)

    @staticmethod
    def set_default_handler(handler: logging.Handler) -> None:
        """
        Set the default handler for all loggers, replacing the current default.

        Args:
            handler: Handler to use as default.

        Example:
            >>> from ds_common_logger_py_lib import Logger
            >>> import logging
            >>> import sys
            >>> Logger.configure()
            >>> custom_handler = logging.StreamHandler(sys.stderr)
            >>> Logger.set_default_handler(custom_handler)
            >>> logger = Logger.get_logger(__name__)
            >>> logger.info("Message goes to stderr via root logger")
        """
        if not Logger._configured:
            raise RuntimeError("Logger must be configured before setting default handler")

        if Logger._default_handler:
            Logger.remove_handler(Logger._default_handler)

        Logger._default_handler = handler
        handler.addFilter(Logger._filter)

        formatter = Logger._create_formatter()
        handler.setFormatter(formatter)

        root_logger = logging.getLogger()
        root_logger.addHandler(handler)

    @staticmethod
    def is_configured() -> bool:
        """Check if Logger has been configured.

        Returns:
            True if Logger has been configured, False otherwise.
        """
        return Logger._configured

    @staticmethod
    def get_managed_loggers() -> set[str]:
        """Get the set of managed loggers.

        Returns:
            The set of registered loggers.
        """
        return Logger._managed_loggers

    @staticmethod
    def get_prefix() -> str:
        """Get the configured prefix.

        Returns:
            The configured prefix.
        """
        return Logger._prefix

    @staticmethod
    def get_format_string() -> str | None:
        """Get the configured format string.

        Returns:
            The configured format string.
        """
        return Logger._format_string

    @staticmethod
    def get_date_format() -> str | None:
        """Get the configured date format.

        Returns:
            The configured date format.
        """
        return Logger._date_format

    @staticmethod
    def _register_managed_logger(logger_name: str) -> None:
        """
        Register a logger name as being managed by this helper.

        This ensures that loggers created via Logger.get_logger()
        are automatically allowed by the filter, regardless of allowed_prefixes.

        Args:
            logger_name: The name of the logger to register.
        """
        Logger._managed_loggers.add(logger_name)

    @staticmethod
    def _normalize_logger_name(name: str) -> str:
        """Normalize internal package names into a dotted namespace.

        Args:
            name: The logger name to normalize.

        Returns:
            The normalized logger name.
        """
        if not name:
            return name

        parts = name.split(".")
        root = parts[0]
        if root.startswith("ds_"):
            root = root.replace("_", ".")
        return ".".join([root, *parts[1:]])

    @staticmethod
    def _create_formatter() -> ExtraFieldsFormatter:
        """Create a formatter with current configuration.

        Returns:
            ExtraFieldsFormatter instance with current configuration.
        """
        format_string = Logger._format_string or Logger.DEFAULT_FORMAT
        if format_string == Logger.DEFAULT_FORMAT_WITH_PREFIX and not Logger._prefix:
            format_string = Logger.DEFAULT_FORMAT
        date_format = Logger._date_format or Logger.DEFAULT_DATE_FORMAT

        template_vars: dict[str, str] = {"prefix": Logger._prefix}

        return ExtraFieldsFormatter(
            fmt=format_string,
            datefmt=date_format,
            template_vars=template_vars,
        )

    @staticmethod
    def _setup_filter() -> None:
        """Apply filter to existing handlers managed by Logger."""
        if Logger._default_handler:
            Logger._default_handler.addFilter(Logger._filter)
        for handler in Logger._handlers:
            handler.addFilter(Logger._filter)

    @staticmethod
    def _update_existing_loggers() -> None:
        """Update root logger handlers managed by Logger with current configuration."""
        formatter = Logger._create_formatter()
        root_logger = logging.getLogger()

        managed_handlers: set[logging.Handler] = set(Logger._handlers)
        if Logger._default_handler:
            managed_handlers.add(Logger._default_handler)

        for handler in root_logger.handlers:
            if handler not in managed_handlers:
                continue

            handler.setFormatter(formatter)
            handler.filters = [f for f in handler.filters if not isinstance(f, LoggerFilter)]
            handler.addFilter(Logger._filter)

            if handler is Logger._default_handler:
                handler.setLevel(Logger._level)

    @staticmethod
    def _apply_logger_levels(previous_levels: dict[str, int] | None = None) -> None:
        """Apply logger-level rules to logger hierarchy.

        Args:
            previous_levels: The previous logger levels.
        """
        previous_levels = previous_levels or {}

        removed_prefixes = set(previous_levels) - set(Logger._logger_levels)
        for prefix in removed_prefixes:
            logging.getLogger(prefix).setLevel(logging.NOTSET)

        for prefix, level in Logger._logger_levels.items():
            logging.getLogger(prefix).setLevel(level)
