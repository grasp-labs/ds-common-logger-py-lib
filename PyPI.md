# ds-common-logger-py-lib

A Python logging library from the ds-common library collection,
providing structured logging with support for extra fields,
class-based loggers, and flexible configuration.

## Installation

Install the package using pip:

```bash
pip install ds-common-logger-py-lib
```

Or using uv (recommended):

```bash
uv pip install ds-common-logger-py-lib
```

## Features

- **Structured Logging**: Extra fields included in log output
- **Logger Helper**: `Logger.configure()` and `Logger.get_logger()` for
  consistent setup
- **Application Configuration**: Prefix, format, handlers, and log levels from
  one place
- **Flexible Output**: Update formats and prefixes at runtime
- **Custom Formatter**: Extra fields are JSON-encoded when possible
- **Standard Library Compatible**: Built on Python's `logging` module

## Quick Start

### Basic Usage

```python
from ds_common_logger_py_lib import Logger

# Initialize logger configuration
Logger.configure()

# Get a logger instance
logger = Logger.get_logger(__name__)

# Log with extra fields
logger.info("Processing data", extra={"user_id": 123, "action": "process"})
```

### Application Configuration

```python
from ds_common_logger_py_lib import Logger
import logging

# Configure at application startup
Logger.configure(
    prefix="MyApp",
    format_string="[%(asctime)s][{prefix}][%(name)s][%(levelname)s]: %(message)s",
    level=logging.INFO
)

logger = Logger.get_logger(__name__)
logger.info("Application started")

# Update prefix at runtime
Logger.set_prefix("MyApp-session123")
logger.info("Session initialized")
```

## Usage Examples

### Setting Log Levels

```python
from ds_common_logger_py_lib import Logger
import logging

Logger.configure(
    level=logging.DEBUG,
    logger_levels={
        "myapp.verbose": logging.DEBUG,
        "myapp.quiet": logging.WARNING,
    },
)

verbose_logger = Logger.get_logger("myapp.verbose")
quiet_logger = Logger.get_logger("myapp.quiet")

verbose_logger.debug("Debug message is visible")
quiet_logger.info("Info message is hidden")
quiet_logger.warning("Warning message is visible")
```

### Multiple Classes with Isolated Loggers

```python
from ds_common_logger_py_lib import Logger

class UserService:
    def create_user(self, username: str):
        logger = Logger.get_logger("services.user")
        logger.info("Creating user", extra={"username": username})

class OrderService:
    def create_order(self, user_id: int):
        logger = Logger.get_logger("services.order")
        logger.info("Creating order", extra={"user_id": user_id})

# Each class has its own logger with distinct names
user_service = UserService()
order_service = OrderService()
```

## Requirements

- Python 3.10 or higher

## Documentation

Full documentation is available at:

- [GitHub Repository](https://github.com/grasp-labs/ds-common-logger-py-lib)

## Development

To contribute or set up a development environment:

```bash
# Clone the repository
git clone https://github.com/grasp-labs/ds-common-logger-py-lib.git
cd ds-common-logger-py-lib

# Install development dependencies
uv sync --all-extras --dev

# Run tests
make test
```

See the
[README](https://github.com/grasp-labs/ds-common-logger-py-lib#readme)
for more information.

## License

This package is licensed under the Apache License 2.0.
See the
[LICENSE-APACHE](https://github.com/grasp-labs/ds-common-logger-py-lib/blob/main/LICENSE-APACHE)
file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/grasp-labs/ds-common-logger-py-lib/issues)
- **Releases**: [GitHub Releases](https://github.com/grasp-labs/ds-common-logger-py-lib/releases)
