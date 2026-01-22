"""
**File:** ``mixin.py``
**Region:** ``ds_common_logger_py_lib``

Description
-----------
Defines a convenience mixin that provides per-class and per-instance loggers,
backed by the package ``Logger`` configuration. Each concrete class receives a
distinct logger name derived from its module and class name.

Example
-------
    >>> from ds_common_logger_py_lib import LoggingMixin, Logger
    >>> import logging
    >>>
    >>> Logger()
    >>>
    >>> class MyClass(LoggingMixin):
    ...     def do_something(self):
    ...         self.log.info("Doing something")
    >>>
    >>> instance = MyClass()
    >>> instance.log.info("Hello, world!")
    [2024-01-15T10:30:45][__main__.MyClass][INFO][mixin.py:24]: Hello, world!
    >>>
    >>> MyClass.set_log_format("%(levelname)s: %(message)s")
    >>> instance.log.info("Formatted message")
    INFO: Formatted message
"""

from __future__ import annotations

import logging
from typing import ClassVar

from .core import Logger


class LoggingMixin:
    """
    Convenience mixin class to provide logger access in classes.

    This mixin provides both class-level and instance-level logger access,
    using the core Logger infrastructure for consistent logging across the application.
    Each class using this mixin gets its own logger instance based on the class's module and name.

    To set a default log level for a class, set the log_level class attribute:

    Example:
        >>> from ds_common_logger_py_lib import LoggingMixin, Logger
        >>> import logging
        >>> Logger()
        >>> class MyClass(LoggingMixin):
        ...     log_level = logging.DEBUG
        ...     def do_something(self):
        ...         self.log.info("Doing something")
        >>> instance = MyClass()
        >>> instance.log.info("Test message")
        [2024-01-15T10:30:45][__main__.MyClass][INFO][mixin.py:59]: Test message
    """

    _loggers: ClassVar[dict[type[LoggingMixin], logging.Logger]] = {}
    log_level: int | None = None

    @classmethod
    def logger(cls, level: int | None = None) -> logging.Logger:
        """
        Get the class logger instance.

        Args:
            level: Optional logging level override. If not provided, uses cls.log_level.

        Returns:
            Configured logger instance for the class.

        Example:
            >>> from ds_common_logger_py_lib import LoggingMixin, Logger
            >>> import logging
            >>> Logger()
            >>> class MyClass(LoggingMixin):
            ...     log_level = logging.DEBUG
            ...     pass
            >>> logger = MyClass.logger()
            >>> logger.info("Class-level log")
            [2024-01-15T10:30:45][__main__.MyClass][INFO][mixin.py:88]: Class-level log
        """
        return cls._get_logger(level)

    @classmethod
    def set_log_level(cls, level: int) -> None:
        """
        Set or update the log level for this class.

        Args:
            level: Logging level to set.

        Example:
            >>> from ds_common_logger_py_lib import LoggingMixin, Logger
            >>> import logging
            >>> Logger()
            >>> class MyClass(LoggingMixin):
            ...     pass
            >>> MyClass.set_log_level(logging.DEBUG)
            >>> logger = MyClass.logger()
            >>> logger.level == logging.DEBUG
            True
        """
        cls.log_level = level
        if cls in cls._loggers:
            logger = cls._loggers[cls]
            logger.setLevel(level)
            for handler in logger.handlers:
                handler.setLevel(level)

    @classmethod
    def set_log_format(
        cls,
        format_string: str | None = None,
        date_format: str | None = None,
    ) -> None:
        """
        Set or update the log format for all loggers.

        This calls Logger.set_log_format() and recreates existing loggers.

        Args:
            format_string: Format string to set. If None, resets to default format.
            date_format: Date format string to set. If None, resets to default date format.

        Example:
            >>> from ds_common_logger_py_lib import LoggingMixin, Logger
            >>> import logging
            >>> Logger()
            >>> class MyClass(LoggingMixin):
            ...     pass
            >>> MyClass.set_log_format("%(levelname)s: %(message)s")
            >>> logger = MyClass.logger()
            >>> logger.info("This will use the custom format")
            INFO: This will use the custom format
        """
        Logger.set_log_format(format_string, date_format)
        if cls in cls._loggers:
            del cls._loggers[cls]

    @classmethod
    def _get_logger(cls, level: int | None = None) -> logging.Logger:
        """
        Get or create the logger for this class.

        Args:
            level: Optional logging level override. Uses cls.log_level if not provided.

        Returns:
            Configured logger instance for the class.

        Example:
            >>> from ds_common_logger_py_lib import LoggingMixin, Logger
            >>> import logging
            >>> Logger()
            >>> class MyClass(LoggingMixin):
            ...     pass
            >>> logger = MyClass._get_logger()
            >>> logger.info("Test message")
            [2024-01-15T10:30:45][__main__.MyClass][INFO][mixin.py:155]: Test message
        """
        if cls not in cls._loggers:
            logger_name = f"{cls.__module__}.{cls.__name__}"
            effective_level = level or cls.log_level
            cls._loggers[cls] = Logger.get_logger(logger_name, effective_level)
        elif level is not None:
            logger = cls._loggers[cls]
            logger.setLevel(level)
            for handler in logger.handlers:
                handler.setLevel(level)
        return cls._loggers[cls]

    @property
    def log(self) -> logging.Logger:
        """
        Get the logger instance for this object.

        Returns:
            Configured logger instance for the object.

        Example:
            >>> from ds_common_logger_py_lib import LoggingMixin, Logger
            >>> import logging
            >>> Logger()
            >>> class MyClass(LoggingMixin):
            ...     log_level = logging.DEBUG
            ...     def do_something(self):
            ...         self.log.info("Doing something")
            >>> instance = MyClass()
            >>> instance.log.info("Test message")
            [2024-01-15T10:30:45][__main__.MyClass][INFO][mixin.py:180]: Test message
        """
        return self.__class__._get_logger()
