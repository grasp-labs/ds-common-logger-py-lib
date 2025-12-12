"""
Example: Multi-class logging with per-class loggers.

Shows how each class gets its own logger with distinct names.
"""

from ds_common_logger_py_lib import LoggingMixin


class UserService(LoggingMixin):
    """User management service."""

    def create_user(self, username: str) -> dict:
        self.log.info("Creating user", extra={"username": username})
        return {"id": 1, "username": username}

    def delete_user(self, user_id: int) -> None:
        self.log.warning("Deleting user", extra={"user_id": user_id})


class OrderService(LoggingMixin):
    """Order management service."""

    def create_order(self, user_id: int, items: list) -> dict:
        self.log.info("Creating order", extra={"user_id": user_id, "item_count": len(items)})
        return {"order_id": 123, "user_id": user_id}

    def cancel_order(self, order_id: int) -> None:
        self.log.warning("Cancelling order", extra={"order_id": order_id})


class PaymentService(LoggingMixin):
    """Payment processing service."""

    def process_payment(self, order_id: int, amount: float) -> bool:
        self.log.info("Processing payment", extra={"order_id": order_id, "amount": amount})
        return True

    def refund_payment(self, payment_id: int) -> None:
        self.log.error("Refunding payment", extra={"payment_id": payment_id})


if __name__ == "__main__":
    user_service = UserService()
    order_service = OrderService()
    payment_service = PaymentService()

    # Each class logs with its own logger name
    user = user_service.create_user("alice")
    order = order_service.create_order(user["id"], ["item1", "item2"])
    payment_service.process_payment(order["order_id"], 99.99)
