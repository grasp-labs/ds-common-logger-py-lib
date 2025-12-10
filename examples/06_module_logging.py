"""
Example: Logging across multiple modules with local imports.

Demonstrates how logger names appear when using imported modules:
- When run directly: logger name shows __main__
- When imported: logger name shows the actual module path (examples.helpers)

This shows the difference between running a script directly vs importing it.
"""

import logging
from ds_common_logger_py_lib import Logger, LoggingMixin

# Import local helper module from the same directory
from helpers import DataValidator, DataTransformer, validate_data_format

Logger(
    level=logging.DEBUG,
    handlers=[logging.FileHandler("examples/example.log")],
)
logger = Logger.get_logger(__name__)


class DataProcessor(LoggingMixin):
    """Main data processor that uses imported modules."""

    def process(self, data: dict) -> dict:
        """Process data using imported validators and transformers."""
        self.log.info("Starting data processing pipeline", extra={"pipeline": "main"})

        if not validate_data_format(data):
            self.log.error("Format validation failed, aborting pipeline")
            return {}

        validator = DataValidator()
        if not validator.validate(data):
            self.log.error("Validation failed, aborting pipeline")
            return {}

        transformer = DataTransformer()
        result = transformer.transform(data)

        self.log.info(
            "Pipeline completed successfully",
            extra={"result_keys": list(result.keys())},
        )
        return result


if __name__ == "__main__":
    logger.info("Application started", extra={"mode": "direct_execution"})

    processor = DataProcessor()
    data = {"name": "alice", "age": 30, "city": "oslo"}

    result = processor.process(data)

    logger.info("Application finished", extra={"result_count": len(result)})
