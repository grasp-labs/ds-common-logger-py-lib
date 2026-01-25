"""
**File:** ``helpers.py``
**Region:** ``ds_common_logger_py_lib``

Description
-----------
Helper module used by example scripts to demonstrate logging in imported code,
including module-level loggers and class-based logging.
"""

from ds_common_logger_py_lib import Logger


logger = Logger.get_logger(__name__)


def validate_data_format(data: dict) -> bool:
    """Validate data format using function-level logger."""
    logger.info("Validating data format", extra={"data_type": type(data).__name__})

    if not data:
        logger.warning("Empty dictionary provided")
        return False

    logger.info("Format validation successful", extra={"key_count": len(data)})
    return True


class DataValidator:
    """Validates data with logging."""

    def validate(self, data: dict) -> bool:
        """Validate data structure."""
        logger.info("Starting validation", extra={"data_keys": list(data.keys())})

        if not data:
            logger.warning("Empty data dictionary")
            return False

        logger.info("Validation successful", extra={"item_count": len(data)})
        return True


class DataTransformer:
    """Transforms data with logging."""

    def transform(self, data: dict) -> dict:
        """Transform data structure."""
        logger.info("Starting transformation", extra={"input_keys": list(data.keys())})

        transformed = {f"transformed_{k}": str(v).upper() for k, v in data.items()}

        logger.debug("Transformation complete", extra={"output_keys": list(transformed.keys())})
        return transformed
