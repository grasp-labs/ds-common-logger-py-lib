"""
**File:** ``__init__.py``
**Region:** ``ds_common_logger_py_lib``

Description
-----------
Package entrypoint that exposes the public API (``Logger``, ``LoggingMixin``)
and the installed package version (``__version__``).

Example
-------
    >>> from ds_common_logger_py_lib import Logger, LoggerConfig
    >>>
    >>> LoggerConfig.configure(
    ...     prefix="Application",
    ...     level=logging.DEBUG
    ... )
    >>> logger = Logger.get_logger(__name__)
    >>>
    >>> logger.info("Hello from ds_common_logger_py_lib")
    [2024-01-15T10:30:45][__main__][INFO][__init__.py:16]: Hello from ds_common_logger_py_lib
    >>>
    >>> class Service(LoggingMixin):
    ...     def foo(self):
    ...         self.log.info("Hello from Service")
    ...         self.log.debug("Debug message - only visible with DEBUG level")
    >>>
    ...     def bar(self):
    ...         self.log.debug("Debug message - only visible with DEBUG level")
    >>>
    >>> Service().foo()
    [2024-01-15T10:30:45][__main__.Service][INFO][mixin.py:180]: Hello from Service
    >>> Service().bar()
    [2024-01-15T10:30:45][__main__.Service][DEBUG][mixin.py:180]: Debug message - only visible with DEBUG level
"""

from importlib.metadata import version

from .config import LoggerConfig, LoggerFilter
from .core import Logger
from .mixin import LoggingMixin

__version__ = version("ds_common_logger_py_lib")

__all__ = ["Logger", "LoggerConfig", "LoggerFilter", "LoggingMixin", "__version__"]
