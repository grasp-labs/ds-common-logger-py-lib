"""
**File:** ``__init__.py``
**Region:** ``ds_common_logger_py_lib``

Description
-----------
Package entrypoint that exposes the public API (``Logger``, ``LoggingMixin``)
and the installed package version (``__version__``).

Example
-------
.. code-block:: python

    from ds_common_logger_py_lib import Logger, LoggingMixin, __version__

    Logger()
    logger = Logger.get_logger(__name__)
    logger.info("Hello from ds_common_logger_py_lib", extra={"version": __version__})


    class Service(LoggingMixin):
        pass

    Service().log.info("Hello from LoggingMixin")
"""

from importlib.metadata import version

from .config import LoggerConfig
from .core import Logger
from .mixin import LoggingMixin

__version__ = version("ds_common_logger_py_lib")

__all__ = ["Logger", "LoggerConfig", "LoggingMixin", "__version__"]
