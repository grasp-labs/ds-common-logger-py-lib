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

from pathlib import Path

from .core import Logger
from .mixin import LoggingMixin

_VERSION_FILE = Path(__file__).parent.parent.parent / "VERSION.txt"
__version__ = _VERSION_FILE.read_text().strip() if _VERSION_FILE.exists() else "0.0.0"

__all__ = ["Logger", "LoggingMixin", "__version__"]
