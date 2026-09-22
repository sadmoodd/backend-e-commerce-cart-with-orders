from dataclasses import dataclass, field
from uuid import UUID, uuid4
from decimal import Decimal
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"


@dataclass
class OrderItem:
    product_id: UUID
    quantity: int
    price_at_purchase: Decimal


@dataclass
class Order:
    id: UUID
    user_id: UUID
    items: list[OrderItem]
    status: OrderStatus = OrderStatus.PENDING
    total: Decimal = Decimal("0")

    def __post_init__(self):
        if self.id is None or not isinstance(self.id, UUID):
            raise ValueError("id must be UUID")
        if self.user_id is None:
            raise ValueError("user_id required")
        if not self.items:
            raise ValueError("Order cannot be empty")
        self.total = sum(
            (item.price_at_purchase * item.quantity for item in self.items),
            Decimal("0"),
        )

    @classmethod
    def from_cart(cls, cart, user_id: UUID) -> "Order":
        """Создать Order из доменного Cart."""
        items = [
            OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=item.price_at_added,
            )
            for item in cart.items
        ]
        return cls(
            id=uuid4(),
            user_id=user_id,
            items=items,
        )