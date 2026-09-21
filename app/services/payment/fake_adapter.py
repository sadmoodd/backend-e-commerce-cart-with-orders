from uuid import UUID, uuid4
from decimal import Decimal
from app.services.payment.gateway import PaymentGateway, PaymentResult


class FakePaymentAdapter(PaymentGateway):
    """Заглушка платёжного шлюза. Всегда успешна."""

    def process_payment(
        self,
        order_id: UUID,
        amount: Decimal,
        details: dict,
    ) -> PaymentResult:
        # имитация успешной оплаты
        return PaymentResult(
            success=True,
            transaction_id=f"fake-{uuid4()}",
        )

    def refund(self, transaction_id: str, amount: Decimal) -> PaymentResult:
        return PaymentResult(
            success=True,
            transaction_id=transaction_id,
        )