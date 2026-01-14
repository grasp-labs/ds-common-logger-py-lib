"""
**File:** ``__init__.py``
**Region:** ``ds_common_logger_py_lib``

Description
-----------
A Python package from the ds_common_logger_py_lib library.

Example
-------
.. code-block:: python

    from ds_common_logger_py_lib import __version__

    print(f"Package version: {__version__}")
"""

from importlib.metadata import version

from .core import Logger
from .mixin import LoggingMixin

__version__ = version("ds_common_logger_py_lib")

__all__ = ["Logger", "LoggingMixin", "__version__"]
