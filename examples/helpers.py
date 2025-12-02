"""
Example helper module: Demonstrates logging in imported modules.

This module shows how logger names appear when modules are imported
(using the actual module path instead of __main__).

Demonstrates both function-level logging and class-level logging with LoggingMixin.
"""

from ds_common_logger_py_lib import Logger, LoggingMixin

# Get a function-level logger for this module
logger = Logger.get_logger(__name__)


def validate_data_format(data: dict) -> bool:
    """Validate data format using function-level logger."""
    logger.info("Validating data format", extra={"data_type": type(data).__name__})

    if not data:
        logger.warning("Empty dictionary provided")
        return False

    logger.info("Format validation successful", extra={"key_count": len(data)})
    return True


class DataValidator(LoggingMixin):
    """Validates data with logging."""

    def validate(self, data: dict) -> bool:
        """Validate data structure."""
        self.log.info("Starting validation", extra={"data_keys": list(data.keys())})

        if not data:
            self.log.warning("Empty data dictionary")
            return False

        self.log.info("Validation successful", extra={"item_count": len(data)})
        return True


class DataTransformer(LoggingMixin):
    """Transforms data with logging."""

    def transform(self, data: dict) -> dict:
        """Transform data structure."""
        self.log.info("Starting transformation", extra={"input_keys": list(data.keys())})

        transformed = {f"transformed_{k}": str(v).upper() for k, v in data.items()}

        self.log.debug("Transformation complete", extra={"output_keys": list(transformed.keys())})
        return transformed
