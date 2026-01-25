"""
**File:** ``04_module_logging.py``
**Region:** ``ds_common_logger_py_lib``

Description
-----------
Example script demonstrating module-level logging and how logger names differ
between direct execution (``__main__``) and imported modules (e.g. ``helpers``).
"""

import logging
import os
import sys

from ds_common_logger_py_lib import Logger

from helpers import DataValidator, DataTransformer, validate_data_format

log_file_path = os.path.join(os.path.dirname(__file__), "example.log")

Logger.configure(
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = Logger.get_logger(__name__)


class DataProcessor:
    """Main data processor that uses imported modules."""

    def __init__(self) -> None:
        self.logger = Logger.get_logger(f"{__name__}.DataProcessor")

    def process(self, data: dict) -> dict:
        """Process data using imported validators and transformers."""
        self.logger.info("Starting data processing pipeline", extra={"pipeline": "main"})

        if not validate_data_format(data):
            self.logger.error("Format validation failed, aborting pipeline")
            return {}

        validator = DataValidator()
        if not validator.validate(data):
            self.logger.error("Validation failed, aborting pipeline")
            return {}

        transformer = DataTransformer()
        result = transformer.transform(data)

        self.logger.info(
            "Pipeline completed successfully",
            extra={"result_keys": list(result.keys())},
        )
        return result


def main() -> None:
    logger.info("Application started", extra={"mode": "direct_execution"})
    processor = DataProcessor()
    data = {"name": "alice", "age": 30, "city": "oslo"}
    result = processor.process(data)
    logger.info("Application finished", extra={"result_count": len(result)})


if __name__ == "__main__":
    main()
