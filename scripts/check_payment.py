from uuid import uuid4
from decimal import Decimal

from app.services.payment import FakePaymentAdapter, PaymentFacade


gateway = FakePaymentAdapter()
facade = PaymentFacade(gateway)

result = facade.pay_order(uuid4(), Decimal("100.50"))
print(f"pay_order: success={result.success}, txn={result.transaction_id}")

refund = facade.refund_order("fake-txn-1", Decimal("50.00"))
print(f"refund: success={refund.success}, txn={refund.transaction_id}")

print("✓ DONE")