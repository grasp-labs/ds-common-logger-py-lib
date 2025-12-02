"""
Example: Real-world scenario showing per-class logger benefits.

Simulates an e-commerce order processing pipeline where multiple
services interact. Each service has its own logger, making it easy
to trace operations across the system.
"""

from ds_common_logger_py_lib import Logger, LoggingMixin

Logger()


class InventoryService(LoggingMixin):
    """Manages product inventory."""

    def check_stock(self, product_id: str, quantity: int) -> bool:
        self.log.info("Checking stock", extra={"product_id": product_id, "quantity": quantity})
        return True

    def reserve_items(self, product_id: str, quantity: int) -> str:
        reservation_id = "res_123"
        self.log.info("Items reserved", extra={"product_id": product_id, "reservation_id": reservation_id})
        return reservation_id


class ShippingService(LoggingMixin):
    """Handles order shipping."""

    def calculate_shipping(self, order_id: str, address: dict) -> float:
        cost = 5.99
        self.log.info("Shipping calculated", extra={"order_id": order_id, "cost": cost})
        return cost

    def create_shipment(self, order_id: str) -> str:
        tracking = "TRACK123"
        self.log.info("Shipment created", extra={"order_id": order_id, "tracking": tracking})
        return tracking


class NotificationService(LoggingMixin):
    """Sends notifications to users."""

    def send_confirmation(self, user_id: str, order_id: str) -> None:
        self.log.info("Sending confirmation", extra={"user_id": user_id, "order_id": order_id})

    def send_shipping_update(self, user_id: str, tracking: str) -> None:
        self.log.info("Sending shipping update", extra={"user_id": user_id, "tracking": tracking})


class OrderProcessor(LoggingMixin):
    """Orchestrates order processing."""

    def __init__(self):
        self.inventory = InventoryService()
        self.shipping = ShippingService()
        self.notifications = NotificationService()

    def process_order(self, user_id: str, product_id: str, quantity: int, address: dict) -> dict:
        self.log.info("Starting order processing", extra={"user_id": user_id, "product_id": product_id})

        # Each service logs with its own name, making it easy to trace the flow
        if not self.inventory.check_stock(product_id, quantity):
            self.log.error("Insufficient stock", extra={"product_id": product_id})
            return {"status": "failed", "reason": "out_of_stock"}

        self.inventory.reserve_items(product_id, quantity)
        self.shipping.calculate_shipping("order_456", address)
        tracking = self.shipping.create_shipment("order_456")

        self.notifications.send_confirmation(user_id, "order_456")
        self.notifications.send_shipping_update(user_id, tracking)

        self.log.info("Order processed successfully", extra={"order_id": "order_456"})
        return {"status": "success", "order_id": "order_456", "tracking": tracking}


if __name__ == "__main__":
    """
    In production logs, you can:
    1. Filter by service: "grep 'InventoryService' logs.txt"
    2. Track a specific order: "grep 'order_456' logs.txt"
    3. Monitor errors per service: filter by level and logger name
    4. Set different log levels per service in production
    """
    processor = OrderProcessor()

    # Process an order - watch how each service logs with its own name
    result = processor.process_order(
        user_id="user_123",
        product_id="prod_456",
        quantity=2,
        address={"city": "Oslo", "country": "Norway"}
    )
