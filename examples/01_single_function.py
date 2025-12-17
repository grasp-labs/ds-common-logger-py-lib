"""
**File:** ``01_single_function.py``
**Region:** ``ds_common_logger_py_lib``

Description
-----------
Example script showing basic logging using ``Logger.get_logger()`` directly from
a single function.
"""

from ds_common_logger_py_lib import Logger


Logger()
logger = Logger.get_logger(__name__)


def process_data(data: dict) -> dict:
    """Process data and log operations."""
    logger.info("Starting data processing", extra={"input_size": len(data)})

    result = {"processed": True, "items": len(data)}

    logger.info("Data processing complete", extra={"output_size": len(result)})
    return result


if __name__ == "__main__":
    data = {"item1": "value1", "item2": "value2"}
    process_data(data)
