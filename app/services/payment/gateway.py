from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class PaymentResult:
    success: bool
    transaction_id: str | None = None
    error_message: str | None = None


class PaymentGateway(ABC):
    """Единый интерфейс для всех платёжных провайдеров."""

    @abstractmethod
    def process_payment(
        self,
        order_id: UUID,
        amount: Decimal,
        details: dict,
    ) -> PaymentResult:
        ...

    @abstractmethod
    def refund(self, transaction_id: str, amount: Decimal) -> PaymentResult:
        ...