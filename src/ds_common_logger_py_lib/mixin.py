"""
File: mixin.py
Description: Logging mixin class for convenient logger access in classes.
Region: packages/logging/python

# Example:

from ds_common_logger_py_lib import LoggingMixin


class MyClass(LoggingMixin):
    def do_something(self):
        self.log.info("Doing something")


instance = MyClass()
instance.log.info("Hello, world!")
"""

import logging
from typing import ClassVar, Optional

from .core import Logger


class LoggingMixin:
    """
    Convenience mixin class to provide logger access in classes.

    This mixin provides both class-level and instance-level logger access,
    using the core Logger infrastructure for consistent logging across the application.
    Each class using this mixin gets its own logger instance based on the class's module and name.

    To set a default log level for a class, set the log_level class attribute:

    Example:
        >>> class MyClass(LoggingMixin):
        ...     log_level = logging.DEBUG  # Set default level for this class
        ...     def do_something(self):
        ...         self.log.info("Doing something")
        >>> instance = MyClass()
        >>> instance.log.info("Test message")
    """

    _loggers: ClassVar[dict[type, logging.Logger]] = {}
    log_level: Optional[int] = None

    @classmethod
    def logger(cls, level: Optional[int] = None) -> logging.Logger:
        """
        Get the class logger instance.

        Args:
            level: Optional logging level override. If not provided, uses cls.log_level.

        Returns:
            Configured logger instance for the class.

        Example:
            >>> class MyClass(LoggingMixin):
            ...     log_level = logging.DEBUG
            ...     pass
            >>> logger = MyClass.logger()
            >>> logger.info("Class-level log")
        """
        return cls._get_logger(level)

    @classmethod
    def set_log_level(cls, level: int) -> None:
        """
        Set or update the log level for this class.

        Args:
            level: Logging level to set.

        Example:
            >>> class MyClass(LoggingMixin):
            ...     pass
            >>> MyClass.set_log_level(logging.DEBUG)
            >>> MyClass.logger().debug("This will now be logged")
        """
        cls.log_level = level
        if cls in cls._loggers:
            logger = cls._loggers[cls]
            logger.setLevel(level)
            for handler in logger.handlers:
                handler.setLevel(level)

    @classmethod
    def _get_logger(cls, level: Optional[int] = None) -> logging.Logger:
        """
        Get or create the logger for this class.

        Args:
            level: Optional logging level override. Uses cls.log_level if not provided.

        Returns:
            Configured logger instance for the class.

        Example:
            >>> class MyClass(LoggingMixin):
            ...     pass
            >>> logger = MyClass._get_logger()
            >>> logger.info("Test message")
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
            >>> class MyClass(LoggingMixin):
            ...     log_level = logging.DEBUG
            ...     def do_something(self):
            ...         self.log.info("Doing something")
            >>> instance = MyClass()
            >>> instance.log.info("Test message")
        """
        return self.__class__._get_logger()
