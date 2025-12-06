"""
Example: Logging with class inheritance.

Demonstrates how LoggingMixin works with inheritance:
- Base class inherits LoggingMixin
- Child classes inherit from base class
- Each class gets its own logger based on its actual class name
- Logger names reflect the actual class, not the base class
"""

from ds_common_logger_py_lib import Logger, LoggingMixin
import logging

Logger()


class BaseService(LoggingMixin):
    """Base service class with logging."""

    log_level = logging.INFO

    def initialize(self) -> None:
        """Initialize the service."""
        self.log.info("Base service initialized", extra={"class": self.__class__.__name__})


class UserService(BaseService):
    """User service inheriting from BaseService."""

    def create_user(self, username: str) -> dict:
        """Create a user."""
        self.log.info("Creating user in UserService", extra={"username": username})
        return {"id": 1, "username": username}


class OrderService(BaseService):
    """Order service inheriting from BaseService."""

    log_level = logging.DEBUG  # Override base class log level

    def create_order(self, user_id: int) -> dict:
        """Create an order."""
        self.log.debug("Debug: Creating order", extra={"user_id": user_id})
        self.log.info("Order created in OrderService", extra={"user_id": user_id})
        return {"order_id": 123, "user_id": user_id}


class PaymentService(BaseService):
    """Payment service inheriting from BaseService."""

    def process_payment(self, amount: float) -> None:
        """Process payment."""
        self.log.info("Processing payment in PaymentService", extra={"amount": amount})


if __name__ == "__main__":
    print("=" * 60)
    print("Inheritance Example: Each class gets its own logger")
    print("=" * 60)

    # Base service
    base = BaseService()
    base.initialize()

    # User service - inherits log_level from BaseService (INFO)
    user_service = UserService()
    user_service.initialize()  # Calls base class method
    user = user_service.create_user("alice")

    # Order service - overrides log_level to DEBUG
    order_service = OrderService()
    order_service.initialize()  # Calls base class method
    order = order_service.create_order(user["id"])

    # Payment service - inherits log_level from BaseService (INFO)
    payment_service = PaymentService()
    payment_service.initialize()  # Calls base class method
    payment_service.process_payment(99.99)

    print("\n" + "=" * 60)
    print("Notice in the logs above:")
    print("- Each class has its own logger name (BaseService, UserService, etc.)")
    print("- Base class methods log with the child class's logger name")
    print("- OrderService overrides log_level to DEBUG, so debug logs appear")
    print("- Other services use INFO level from BaseService")
    print("=" * 60)

