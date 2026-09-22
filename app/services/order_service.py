from uuid import UUID

from app.domain.order import Order
from app.domain.exceptions import ProductNotInCartError
from app.db.repositories.cart_repo import CartRepository
from app.db.repositories.order_repo import OrderRepository
from app.services.payment import PaymentFacade


class EmptyCartError(ValueError):
    pass


class PaymentFailedError(ValueError):
    pass


class OrderService:
    def __init__(
        self,
        cart_repo: CartRepository,
        order_repo: OrderRepository,
        payment: PaymentFacade,
    ):
        self.cart_repo = cart_repo
        self.order_repo = order_repo
        self.payment = payment

    def checkout(self, user_id: UUID) -> Order:
        cart = self.cart_repo.get_by_user_id(user_id)
        if cart is None or len(cart) == 0:
            raise EmptyCartError("Корзина пуста")

        order = Order.from_cart(cart, user_id)

        payment_result = self.payment.pay_order(order.id, order.total)
        if not payment_result.success:
            order.status = order.status.FAILED
            self.order_repo.save(order)
            raise PaymentFailedError("Платёж не прошёл")

        order.status = order.status.PAID
        self.order_repo.save(order)

        # очистить корзину
        self.cart_repo.delete(cart.id)

        return order