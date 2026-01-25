"""
**File:** ``__init__.py``
**Region:** ``ds_common_logger_py_lib``

Description
-----------
Package entrypoint that exposes the public API (``Logger``, ``LoggerFilter``)
and the installed package version (``__version__``).

Example
-------
    >>> from ds_common_logger_py_lib import Logger
    >>> import logging
    >>>
    >>> Logger.configure(
    ...     prefix="Application",
    ...     level=logging.DEBUG
    ... )
    >>> logger = Logger.get_logger(__name__)
    >>>
    >>> logger.info("Hello from ds_common_logger_py_lib")
    [2024-01-15T10:30:45][__main__][INFO][__init__.py:16]: Hello from ds_common_logger_py_lib
"""

from importlib.metadata import version

from .core import Logger
from .formatter import LoggerFilter

__version__ = version("ds_common_logger_py_lib")

__all__ = ["Logger", "LoggerFilter", "__version__"]
