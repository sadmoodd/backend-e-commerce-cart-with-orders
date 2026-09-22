from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.order import Order, OrderItem, OrderStatus
from app.db.models.order import OrderModel, OrderItemModel


class OrderRepository:
    def __init__(self, session: Session):
        self.session = session

    def _to_domain(self, model: OrderModel) -> Order:
        items = [
            OrderItem(
                product_id=UUID(item.product_id),
                quantity=item.quantity,
                price_at_purchase=item.price_at_purchase,
            )
            for item in model.items
        ]
        return Order(
            id=UUID(model.id),
            user_id=UUID(model.user_id),
            items=items,
            status=OrderStatus(model.status),
            total=model.total,
        )

    def _to_model(self, domain: Order) -> OrderModel:
        model = OrderModel(
            id=str(domain.id),
            user_id=str(domain.user_id),
            status=domain.status.value,
            total=domain.total,
        )
        model.items = [
            OrderItemModel(
                id=str(__import__("uuid").uuid4()),
                order_id=str(domain.id),
                product_id=str(item.product_id),
                quantity=item.quantity,
                price_at_purchase=item.price_at_purchase,
            )
            for item in domain.items
        ]
        return model

    def save(self, order: Order) -> None:
        model = self._to_model(order)
        self.session.add(model)
        self.session.commit()

    def get_by_id(self, order_id: UUID) -> Order | None:
        model = self.session.get(OrderModel, str(order_id))
        if model is None:
            return None
        return self._to_domain(model)