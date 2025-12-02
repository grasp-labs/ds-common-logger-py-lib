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

- **Structured Logging**: Built-in support for extra fields in log messages
- **Class-Based Loggers**: `LoggingMixin` provides automatic logger setup for classes
- **Per-Class Isolation**: Each class gets its own logger instance
  with distinct names
- **Flexible Configuration**: Set log levels at class level, instance level, or per-call
- **Custom Formatter**: Includes extra fields in JSON format for better log parsing
- **Standard Library Compatible**: Built on Python's `logging` module

## Quick Start

### Basic Usage

```python
from ds_common_logger_py_lib import Logger

# Initialize logger configuration
Logger()

# Get a logger instance
logger = Logger.get_logger(__name__)

# Log with extra fields
logger.info("Processing data", extra={"user_id": 123, "action": "process"})
```

### Using LoggingMixin

```python
from ds_common_logger_py_lib import LoggingMixin
import logging

class UserService(LoggingMixin):
    log_level = logging.INFO

    def create_user(self, username: str) -> dict:
        self.log.info("Creating user", extra={"username": username})
        return {"id": 1, "username": username}

# Use the service
service = UserService()
service.create_user("alice")
```

## Usage Examples

### Setting Log Levels

```python
from ds_common_logger_py_lib import LoggingMixin
import logging

class MyService(LoggingMixin):
    log_level = logging.DEBUG  # Set default level for the class

    def process(self):
        self.log.debug("Debug message")
        self.log.info("Info message")

# Or change level at runtime
MyService.set_log_level(logging.WARNING)

# Or override per call
logger = MyService.logger(level=logging.DEBUG)
logger.debug("This will be shown")
```

### Multiple Classes with Isolated Loggers

```python
from ds_common_logger_py_lib import LoggingMixin

class UserService(LoggingMixin):
    def create_user(self, username: str):
        self.log.info("Creating user", extra={"username": username})

class OrderService(LoggingMixin):
    def create_order(self, user_id: int):
        self.log.info("Creating order", extra={"user_id": user_id})

# Each class has its own logger with distinct names
user_service = UserService()
order_service = OrderService()
```

## Requirements

- Python 3.9 or higher

## Documentation

Full documentation is available at:

- [GitHub Repository](https://github.com/grasp-labs/ds-common-logger-py-lib)
- [Documentation Site](https://grasp-labs.github.io/ds-common-logger-py-lib/)

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

This package is licensed under the MIT License.
See the
[LICENSE](https://github.com/grasp-labs/ds-common-logger-py-lib/blob/main/LICENSE)
file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/grasp-labs/ds-common-logger-py-lib/issues)
- **Releases**: [GitHub Releases](https://github.com/grasp-labs/ds-common-logger-py-lib/releases)
