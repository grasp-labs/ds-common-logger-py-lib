"""
**File:** ``06_multi_service_app.py``
**Region:** ``ds_common_logger_py_lib``

Description
-----------
Example showing a real-world multi-service application where the main app
configures logging with a prefix, and multiple services/packages use
the logger without knowing about the app configuration.

This demonstrates the key use case: applications need control over logging
format and handlers, while packages can use the logger transparently.
"""

import logging
from typing import Any

from ds_common_logger_py_lib import Logger

Logger.configure(
    prefix="OrderService",
    format_string="[%(asctime)s][{prefix}][%(name)s][%(levelname)s]: %(message)s",
    date_format="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
# ============================================================================
# Service 1: Inventory Service (from a package)
# ============================================================================


class InventoryService:
    """
    Inventory service from a shared package.

    This service doesn't know about the application's logging configuration,
    but automatically gets the [OrderService] prefix and format.
    """

    def __init__(self):
        self.logger = Logger.get_logger(f"{__name__}.InventoryService")

    def check_stock(self, product_id: str, quantity: int) -> bool:
        self.logger.info(
            "Checking stock availability",
            extra={"product_id": product_id, "requested_quantity": quantity},
        )
        in_stock = quantity <= 100
        self.logger.info(
            "Stock check complete",
            extra={"product_id": product_id, "in_stock": in_stock},
        )
        return in_stock

    def reserve_items(self, product_id: str, quantity: int) -> str:
        reservation_id = f"res_{product_id}_{quantity}"
        self.logger.info(
            "Items reserved",
            extra={
                "product_id": product_id,
                "quantity": quantity,
                "reservation_id": reservation_id,
            },
        )
        return reservation_id


# ============================================================================
# Service 2: Payment Service (from a package)
# ============================================================================


class PaymentService:
    """
    Payment service from a shared package.

    This service uses Logger.get_logger() and automatically
    gets the application's logging configuration.
    """

    def __init__(self):
        self.logger = Logger.get_logger(f"{__name__}.PaymentService")

    def process_payment(self, order_id: str, amount: float, currency: str = "USD") -> dict[str, Any]:
        self.logger.info(
            "Processing payment",
            extra={"order_id": order_id, "amount": amount, "currency": currency},
        )

        payment_id = f"pay_{order_id}"
        self.logger.info(
            "Payment processed successfully",
            extra={"order_id": order_id, "payment_id": payment_id},
        )

        return {"payment_id": payment_id, "status": "success"}


# ============================================================================
# Service 3: Shipping Service (from a package)
# ============================================================================


class ShippingService:
    """
    Shipping service from a shared package.

    Automatically gets the application's configuration.
    """

    def __init__(self):
        self.logger = Logger.get_logger(f"{__name__}.ShippingService")

    def calculate_shipping(self, order_id: str, address: dict[str, Any]) -> float:
        self.logger.info(
            "Calculating shipping cost",
            extra={"order_id": order_id, "address": address},
        )

        cost = 5.99
        self.logger.info(
            "Shipping cost calculated",
            extra={"order_id": order_id, "cost": cost},
        )
        return cost

    def create_shipment(self, order_id: str) -> str:
        tracking_number = f"TRACK_{order_id}"
        self.logger.info(
            "Shipment created",
            extra={"order_id": order_id, "tracking_number": tracking_number},
        )
        return tracking_number


# ============================================================================
# Main Application: Order Processor
# ============================================================================


class OrderProcessor:
    """
    Main application service that orchestrates order processing.

    This is part of the main application and gets the same configuration.
    """

    def __init__(self):
        self.logger = Logger.get_logger(f"{__name__}.OrderProcessor")
        self.inventory = InventoryService()
        self.payment = PaymentService()
        self.shipping = ShippingService()

    def process_order(
        self,
        user_id: str,
        product_id: str,
        quantity: int,
        address: dict[str, Any],
    ) -> dict[str, Any]:
        order_id = f"order_{user_id}_{product_id}"

        self.logger.info(
            "Starting order processing",
            extra={
                "order_id": order_id,
                "user_id": user_id,
                "product_id": product_id,
                "quantity": quantity,
            },
        )

        if not self.inventory.check_stock(product_id, quantity):
            self.logger.error(
                "Order failed: insufficient stock",
                extra={"order_id": order_id, "product_id": product_id},
            )
            return {"status": "failed", "reason": "out_of_stock"}

        reservation_id = self.inventory.reserve_items(product_id, quantity)
        payment_result = self.payment.process_payment(order_id, 99.99)
        shipping_cost = self.shipping.calculate_shipping(order_id, address)
        tracking_number = self.shipping.create_shipment(order_id)

        self.logger.info(
            "Order processed successfully",
            extra={
                "order_id": order_id,
                "reservation_id": reservation_id,
                "payment_id": payment_result["payment_id"],
                "tracking_number": tracking_number,
                "shipping_cost": shipping_cost,
            },
        )

        return {
            "status": "success",
            "order_id": order_id,
            "tracking_number": tracking_number,
        }


def main() -> None:
    processor = OrderProcessor()

    _ = processor.process_order(
        user_id="user_123",
        product_id="prod_456",
        quantity=2,
        address={"city": "Oslo", "country": "Norway", "zip": "0150"},
    )


if __name__ == "__main__":
    main()
