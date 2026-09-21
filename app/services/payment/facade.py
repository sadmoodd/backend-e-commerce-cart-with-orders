from uuid import UUID
from decimal import Decimal

from app.services.payment.gateway import PaymentGateway, PaymentResult


class PaymentFacade:
    """Упрощённый вход для оплаты заказа."""

    def __init__(self, gateway: PaymentGateway):
        self.gateway = gateway

    def pay_order(self, order_id: UUID, amount: Decimal) -> PaymentResult:
        return self.gateway.process_payment(order_id, amount, {})

    def refund_order(self, transaction_id: str, amount: Decimal) -> PaymentResult:
        return self.gateway.refund(transaction_id, amount)